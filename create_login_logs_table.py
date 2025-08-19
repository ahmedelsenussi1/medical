import sqlite3
import os
from datetime import datetime

# مسار ملف قاعدة البيانات
db_path = os.path.join('c:\\Users\\Acer\\Desktop\\Medicalcare\\instance', 'clinic.db')

# التحقق من وجود قاعدة البيانات
if not os.path.exists(db_path):
    print(f"ملف قاعدة البيانات غير موجود في {db_path}")
    exit(1)

try:
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # التحقق من وجود جدول سجلات تسجيل الدخول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_logs'")
    if cursor.fetchone():
        print("جدول سجلات تسجيل الدخول موجود بالفعل")
        
        # التحقق من وجود الأعمدة الجديدة
        cursor.execute("PRAGMA table_info(login_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # إضافة أعمدة جديدة إذا لم تكن موجودة
        if 'session_id' not in columns:
            print("إضافة عمود session_id...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN session_id VARCHAR(50)")
        
        if 'device_type' not in columns:
            print("إضافة عمود device_type...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN device_type VARCHAR(50)")
        
        if 'browser' not in columns:
            print("إضافة عمود browser...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN browser VARCHAR(50)")
        
        if 'os' not in columns:
            print("إضافة عمود os...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN os VARCHAR(50)")
        
        if 'session_duration' not in columns:
            print("إضافة عمود session_duration...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN session_duration INTEGER")
        
        if 'status' not in columns:
            print("إضافة عمود status...")
            cursor.execute("ALTER TABLE login_logs ADD COLUMN status VARCHAR(20) DEFAULT 'success'")
        
    else:
        # إنشاء جدول سجلات تسجيل الدخول
        print("جاري إنشاء جدول سجلات تسجيل الدخول...")
        cursor.execute('''
        CREATE TABLE login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action VARCHAR(20) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(50),
            user_agent VARCHAR(255),
            session_id VARCHAR(50),
            device_type VARCHAR(50),
            browser VARCHAR(50),
            os VARCHAR(50),
            session_duration INTEGER,
            status VARCHAR(20) DEFAULT 'success',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        print("تم إنشاء جدول سجلات تسجيل الدخول بنجاح")
    
    # إنشاء فهارس لتحسين الأداء
    print("إنشاء فهارس لتحسين الأداء...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_logs_action ON login_logs (action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_logs_timestamp ON login_logs (timestamp)")
    
    conn.commit()
    conn.close()
    print("تم تحديث قاعدة البيانات بنجاح")
    
except sqlite3.Error as e:
    print(f"خطأ في SQLite: {e}")
except Exception as e:
    print(f"خطأ: {e}")