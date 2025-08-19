import sqlite3
import os

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
    
    # التحقق من وجود جدول العلاجات
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='treatments'")
    if cursor.fetchone():
        print("جدول العلاجات موجود، جاري التحقق من الأعمدة...")
        
        # الحصول على معلومات الأعمدة الحالية
        cursor.execute("PRAGMA table_info(treatments)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # التحقق من وجود الأعمدة المطلوبة وإضافتها إذا كانت غير موجودة
        required_columns = {
            'start_date': 'DATETIME',
            'end_date': 'DATETIME',
            'instructions': 'TEXT',
            'notes': 'TEXT'
        }
        
        for column_name, column_type in required_columns.items():
            if column_name not in column_names:
                print(f"إضافة العمود {column_name} من النوع {column_type}...")
                cursor.execute(f"ALTER TABLE treatments ADD COLUMN {column_name} {column_type}")
                print(f"تم إضافة العمود {column_name} بنجاح")
        
        print("تم تحديث جدول العلاجات بنجاح")
    else:
        print("جدول العلاجات غير موجود، جاري إنشاء الجدول...")
        
        # إنشاء جدول العلاجات
        cursor.execute('''
        CREATE TABLE treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            medication_name VARCHAR(100) NOT NULL,
            dosage VARCHAR(50) NOT NULL,
            frequency VARCHAR(50),
            start_date DATETIME,
            end_date DATETIME,
            instructions TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
        ''')
        print("تم إنشاء جدول العلاجات بنجاح")
    
    conn.commit()
    conn.close()
    print("تم تحديث قاعدة البيانات بنجاح")
    
except sqlite3.Error as e:
    print(f"خطأ في SQLite: {e}")
except Exception as e:
    print(f"خطأ: {e}")