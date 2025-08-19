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
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(treatments)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'frequency' not in columns:
        # Add the frequency column to the treatments table
        cursor.execute("ALTER TABLE treatments ADD COLUMN frequency VARCHAR(50)")
        conn.commit()
        print("Column 'frequency' added to treatments table successfully")
    else:
        print("Column 'frequency' already exists in treatments table")
    
    conn.close()
    print("Database updated successfully")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")