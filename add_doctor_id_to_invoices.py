import sqlite3
import os

# Path to the database file
db_path = os.path.join('c:\\Users\\Acer\\Desktop\\Medicalcare\\instance', 'clinic.db')

# Check if the database exists
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the doctor_id column already exists in the invoices table
    cursor.execute("PRAGMA table_info(invoices)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'doctor_id' not in columns:
        # Add the doctor_id column to the invoices table
        cursor.execute("ALTER TABLE invoices ADD COLUMN doctor_id INTEGER REFERENCES doctors(id)")
        conn.commit()
        print("Column 'doctor_id' added to invoices table successfully")
    else:
        print("Column 'doctor_id' already exists in invoices table")
    
    conn.close()
    print("Database updated successfully")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")