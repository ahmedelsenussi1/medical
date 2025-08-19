from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import os
from models import db, User, Settings, LoginLog
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
import json
import uuid

# إنشاء تطبيق Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد قاعدة البيانات
db.init_app(app)
migrate = Migrate(app, db)

# إعداد نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تسجيل البلوبرنت
try:
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.patients import patients_bp
    from routes.doctors import doctors_bp
    from routes.appointments import appointments_bp
    from routes.medical_tests import medical_tests_bp
    from routes.treatments import treatments_bp
    from routes.invoices import invoices_bp
    from routes.reports import reports_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(doctors_bp, url_prefix='/doctors')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(medical_tests_bp, url_prefix='/medical_tests')
    app.register_blueprint(treatments_bp, url_prefix='/treatments')
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    app.register_blueprint(reports_bp, url_prefix='/reports')
except ImportError as e:
    print(f"ImportError: {e}")
    pass

# الصفحة الرئيسية
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', current_year=datetime.now().year)

# لوحة التحكم
@app.route('/dashboard')
@login_required
def dashboard():
    # بيانات وهمية للعرض
    stats = {
        'total_patients': 0,
        'today_appointments': 0,
        'total_doctors': 0,
        'unpaid_bills': 0
    }
    today_appointments = []
    recent_patients = []
    
    return render_template('dashboard.html', stats=stats, 
                          today_appointments=today_appointments,
                          recent_patients=recent_patients)

# Initialize Elasticsearch client
try:
    es = Elasticsearch(['http://localhost:9200'])
    es_enabled = True
except Exception as e:
    print(f"Elasticsearch connection error: {e}")
    es_enabled = False

# Add this function to index login logs in Elasticsearch
def index_login_log(log):
    if not es_enabled:
        return
    
    try:
        # Create a document for Elasticsearch
        doc = {
            'user_id': log.user_id,
            'username': log.user.username,
            'role': log.user.role,
            'action': log.action,
            'timestamp': log.timestamp.isoformat(),
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'session_id': str(uuid.uuid4()) if log.action == 'login' else None
        }
        
        # Index the document
        es.index(index='login_logs', document=doc, id=str(log.id))
    except Exception as e:
        print(f"Elasticsearch indexing error: {e}")

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        
        # تسجيل عملية الدخول الحقيقية
        log_entry = LoginLog(
            user_id=user.id,
            action='login',
            ip_address=request.remote_addr or '127.0.0.1',
            user_agent=request.user_agent.string if request.user_agent else 'Unknown'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        # Index in Elasticsearch
        index_login_log(log_entry)
        
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', current_year=datetime.now().year)

# تسجيل الخروج
@app.route('/logout')
@login_required
def logout():
    # تسجيل عملية الخروج الحقيقية
    log_entry = LoginLog(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr or '127.0.0.1',
        user_agent=request.user_agent.string if request.user_agent else 'Unknown'
    )
    db.session.add(log_entry)
    db.session.commit()
    
    # Index in Elasticsearch
    index_login_log(log_entry)
    
    logout_user()
    return redirect(url_for('index'))

# إدارة المستخدمين
@app.route('/users')
@login_required
def users():
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('users/index.html', users=users)

# إضافة مستخدم
@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل', 'danger')
            return redirect(url_for('add_user'))
        
        # Create new user
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('users'))
    
    return render_template('users/add.html')

# الإعدادات
@app.route('/settings')
@login_required
def settings():
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    # الحصول على الإعدادات الحالية
    current_settings = Settings.query.first()
    
    return render_template('settings.html', settings=current_settings)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    # الحصول على الإعدادات الحالية
    settings = Settings.query.first()
    
    # تحديث الإعدادات من النموذج
    settings.clinic_name = request.form.get('clinic_name')
    settings.clinic_phone = request.form.get('clinic_phone')
    settings.clinic_address = request.form.get('clinic_address')
    settings.appointment_interval = int(request.form.get('appointment_interval'))
    settings.working_hours_start = request.form.get('working_hours_start')
    settings.working_hours_end = request.form.get('working_hours_end')
    
    # حفظ التغييرات
    db.session.commit()
    
    flash('تم تحديث الإعدادات بنجاح', 'success')
    return redirect(url_for('settings'))

# الملف الشخصي
@app.route('/profile')
@login_required
def profile():
    return render_template('profile/index.html', user=current_user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = current_user
    
    # تحديث بيانات المستخدم
    if request.form.get('username'):
        user.username = request.form.get('username')
    
    # تحديث كلمة المرور إذا تم توفيرها
    new_password = request.form.get('new_password')
    if new_password and new_password.strip():
        user.set_password(new_password)
    
    db.session.commit()
    flash('تم تحديث الملف الشخصي بنجاح', 'success')
    return redirect(url_for('profile'))

# تغيير كلمة المرور للمستخدم
@app.route('/users/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_user_password(user_id):
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('يرجى إدخال كلمة المرور الجديدة وتأكيدها', 'danger')
            return redirect(url_for('change_user_password', user_id=user_id))
        
        if new_password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'danger')
            return redirect(url_for('change_user_password', user_id=user_id))
        
        user.set_password(new_password)
        db.session.commit()
        
        flash('تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('users'))
    
    return render_template('users/change_password.html', user=user)

# تعديل المستخدم
@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        
        # Check if username already exists and it's not the current user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('اسم المستخدم موجود بالفعل', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))
        
        # Update user data
        user.username = username
        user.role = role
        
        db.session.commit()
        
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('users'))
    
    return render_template('users/edit.html', user=user)

# حذف المستخدم
@app.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting your own account
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'danger')
        return redirect(url_for('users'))
    
    if request.method == 'POST':
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'تم حذف المستخدم {user.username} بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء حذف المستخدم: {str(e)}', 'danger')
        
        return redirect(url_for('users'))
    
    return render_template('users/delete_confirm.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        # Force create the login_log table if it doesn't exist
        db.create_all()
        
        # Rest of your initialization code
        if not os.path.exists('instance/clinic.db'):
            # إنشاء مستخدم مدير افتراضي
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='مدير')
                admin.set_password('admin123')
                
                # إنشاء مستخدم طبيب للاختبار
                doctor = User(username='dialibrahim', role='طبيب')
                doctor.set_password('doctor123')
                
                # إنشاء إعدادات افتراضية
                default_settings = Settings(
                    clinic_name="عيادة الرعاية الطبية",
                    clinic_phone="0123456789",
                    clinic_address="المدينة - الشارع الرئيسي",
                    appointment_interval=30,
                    working_hours_start="08:00",
                    working_hours_end="17:00"
                )
                
                db.session.add(admin)
                db.session.add(doctor)
                db.session.add(default_settings)
                db.session.commit()
    
    app.run(debug=True)