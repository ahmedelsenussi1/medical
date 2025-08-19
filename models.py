from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # طبيب، موظف استقبال، مدير
    doctor = db.relationship('Doctor', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# تعديل العلاقات في نموذج المريض لتضمين cascade="all, delete-orphan"

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    medical_history = db.Column(db.Text)
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات مع تفعيل الحذف التلقائي للسجلات المرتبطة
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan")
    medical_tests = db.relationship('MedicalTest', backref='patient', lazy=True, cascade="all, delete-orphan")
    treatments = db.relationship('Treatment', backref='patient', lazy=True, cascade="all, delete-orphan")
    bills = db.relationship('Billing', backref='patient', lazy=True, cascade="all, delete-orphan")
    # Remove the backref here since it's already defined in the Invoice model
    invoices = db.relationship('Invoice', foreign_keys='Invoice.patient_id', lazy=True, cascade="all, delete-orphan")

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    work_schedule = db.Column(db.Text)
    percentage = db.Column(db.Integer, default=50)  # Add this line for doctor's percentage
    
    # Update relationships to cascade delete
    # Update relationships to use foreign_keys instead of backref
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    treatments = db.relationship('Treatment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    # Change this to use foreign_keys without backref
    invoices = db.relationship('Invoice', foreign_keys='Invoice.doctor_id', lazy=True, cascade="all, delete-orphan")

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='مؤكد')  # مؤكد، ملغي، منجز
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedicalTest(db.Model):
    __tablename__ = 'medical_tests'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.DateTime, nullable=False)
    results = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Add this to your existing models.py

class Treatment(db.Model):
    __tablename__ = 'treatments'  # Explicitly define table name
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)  # تغيير nullable=False إلى اختياري
    end_date = db.Column(db.DateTime)
    instructions = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships are already defined in the Patient and Doctor models
    # No need to redefine them here
class Billing(db.Model):
    __tablename__ = 'billing'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='غير مدفوع')  # مدفوع، غير مدفوع، جزئي
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(100), nullable=False, default="عيادة الرعاية الطبية")
    clinic_phone = db.Column(db.String(20))
    clinic_address = db.Column(db.String(200))
    appointment_interval = db.Column(db.Integer, default=30)  # بالدقائق
    working_hours_start = db.Column(db.String(5), default="08:00")
    working_hours_end = db.Column(db.String(5), default="17:00")

# Add this after your other models

# Add doctor_id to the Invoice model
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Make sure this exists
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=True)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='غير مدفوعة')  # غير مدفوعة، مدفوعة، مدفوعة جزئياً
    payment_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Keep this relationship definition
    patient = db.relationship('Patient', foreign_keys=[patient_id])
    doctor = db.relationship('Doctor', foreign_keys=[doctor_id])
    appointment = db.relationship('Appointment', backref=db.backref('invoice', lazy=True, uselist=False))
    treatment = db.relationship('Treatment', backref=db.backref('invoice', lazy=True, uselist=False))

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # 'login' or 'logout'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    session_duration = db.Column(db.Integer, nullable=True)  # مدة الجلسة بالدقائق
    
    # Relationship
    user = db.relationship('User', backref=db.backref('login_logs', lazy=True))