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
    
    # حفظ البيانات الموجودة قبل حذف الجدول (إذا كان موجودًا)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='treatments'")
    if cursor.fetchone():
        print("جاري حفظ البيانات الموجودة...")
        cursor.execute("SELECT * FROM treatments")
        existing_data = cursor.fetchall()
        
        # الحصول على أسماء الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(treatments)")
        columns_info = cursor.fetchall()
        column_names = [column[1] for column in columns_info]
        
        print(f"تم العثور على {len(existing_data)} سجل")
        print(f"الأعمدة الموجودة: {column_names}")
        
        # حذف الجدول الحالي
        print("جاري حذف جدول العلاجات الحالي...")
        cursor.execute("DROP TABLE IF EXISTS treatments")
    else:
        existing_data = []
        column_names = []
    
    # إنشاء جدول العلاجات مع جميع الأعمدة المطلوبة
    print("جاري إنشاء جدول العلاجات الجديد مع جميع الأعمدة المطلوبة...")
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
    
    # استعادة البيانات إذا كانت موجودة
    if existing_data and 'id' in column_names:
        print("جاري استعادة البيانات...")
        for record in existing_data:
            # إنشاء قاموس للبيانات
            record_dict = {column_names[i]: record[i] for i in range(len(column_names))}
            
            # إنشاء قائمة بالأعمدة والقيم للإدراج
            columns = []
            values = []
            placeholders = []
            
            for col in ['patient_id', 'doctor_id', 'medication_name', 'dosage', 'frequency', 
                        'start_date', 'end_date', 'instructions', 'notes', 'created_at']:
                if col in record_dict:
                    columns.append(col)
                    values.append(record_dict[col])
                    placeholders.append('?')
            
            # إدراج البيانات في الجدول الجديد
            if columns:
                sql = f"INSERT INTO treatments ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, values)
    
    conn.commit()
    conn.close()
    print("تم إعادة بناء جدول العلاجات بنجاح")
    
except sqlite3.Error as e:
    print(f"خطأ في SQLite: {e}")
except Exception as e:
    print(f"خطأ: {e}")