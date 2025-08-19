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
    
    # Check if the percentage column already exists in the doctors table
    cursor.execute("PRAGMA table_info(doctors)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'percentage' not in columns:
        # Add the percentage column to the doctors table
        cursor.execute("ALTER TABLE doctors ADD COLUMN percentage INTEGER DEFAULT 50")
        conn.commit()
        print("Column 'percentage' added to doctors table successfully")
    else:
        print("Column 'percentage' already exists in doctors table")
    
    # Close the connection
    conn.close()
    print("Database updated successfully")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")