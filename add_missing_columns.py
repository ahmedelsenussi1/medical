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
    
    # Check if the treatments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='treatments'")
    if not cursor.fetchone():
        print("The treatments table doesn't exist. Creating it...")
        cursor.execute('''
        CREATE TABLE treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            medication_name VARCHAR(100) NOT NULL,
            dosage VARCHAR(50) NOT NULL,
            frequency VARCHAR(50),
            start_date DATETIME NOT NULL,
            end_date DATETIME,
            instructions TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
        ''')
        print("Treatments table created successfully")
    else:
        # Check existing columns in the treatments table
        cursor.execute("PRAGMA table_info(treatments)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {columns}")
        
        # Add missing columns if they don't exist
        missing_columns = {
            'frequency': 'VARCHAR(50)',
            'start_date': 'DATETIME',
            'end_date': 'DATETIME',
            'instructions': 'TEXT',
            'notes': 'TEXT',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }
        
        for column_name, column_type in missing_columns.items():
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE treatments ADD COLUMN {column_name} {column_type}")
                print(f"Column '{column_name}' added to treatments table")
    
    conn.commit()
    conn.close()
    print("Database updated successfully")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")