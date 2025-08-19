from flask import Flask
from models import db, User, Settings
from datetime import datetime

# إنشاء تطبيق مؤقت للتهيئة
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()
    
    # التحقق من وجود مستخدم مدير
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        # إنشاء مستخدم مدير افتراضي
        admin_user = User(
            username='admin',
            role='مدير'
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        
        # إنشاء إعدادات افتراضية
        default_settings = Settings(
            clinic_name="عيادة الرعاية الطبية",
            clinic_phone="0123456789",
            clinic_address="المدينة - الشارع الرئيسي",
            appointment_interval=30,
            working_hours_start="08:00",
            working_hours_end="17:00"
        )
        
        db.session.add(default_settings)
        db.session.commit()
        
        print('تم إنشاء مستخدم مدير افتراضي:')
        print('اسم المستخدم: admin')
        print('كلمة المرور: admin123')
        print('تم إنشاء الإعدادات الافتراضية للنظام')
    else:
        print('مستخدم المدير موجود بالفعل')
    
    print('تم إنشاء قاعدة البيانات بنجاح')