import sqlite3
import os
from datetime import datetime

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
    
    # Check if the invoices table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
    if cursor.fetchone():
        print("Invoices table already exists")
    else:
        # Create the invoices table
        print("Creating invoices table...")
        cursor.execute('''
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_id INTEGER,
            treatment_id INTEGER,
            invoice_date DATETIME NOT NULL,
            due_date DATETIME,
            amount FLOAT NOT NULL,
            tax FLOAT DEFAULT 0,
            discount FLOAT DEFAULT 0,
            total_amount FLOAT NOT NULL,
            status VARCHAR(20) DEFAULT 'غير مدفوعة',
            payment_method VARCHAR(50),
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (appointment_id) REFERENCES appointments (id),
            FOREIGN KEY (treatment_id) REFERENCES treatments (id)
        )
        ''')
        print("Invoices table created successfully")
    
    conn.commit()
    conn.close()
    print("Database updated successfully")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")