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
    
    # التحقق من وجود عمود session_duration في جدول login_logs
    cursor.execute("PRAGMA table_info(login_logs)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'session_duration' not in columns:
        # إضافة عمود session_duration إلى جدول login_logs
        cursor.execute("ALTER TABLE login_logs ADD COLUMN session_duration INTEGER")
        conn.commit()
        print("تمت إضافة عمود 'session_duration' إلى جدول login_logs بنجاح")
    else:
        print("عمود 'session_duration' موجود بالفعل في جدول login_logs")
    
    # إغلاق الاتصال
    conn.close()
    print("تم تحديث قاعدة البيانات بنجاح")
    
except sqlite3.Error as e:
    print(f"خطأ في SQLite: {e}")
except Exception as e:
    print(f"حدث خطأ: {e}")