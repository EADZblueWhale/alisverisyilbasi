from app import app, db
import sqlite3

with app.app_context():
    # Get database path
    db_path = 'instance/buyulu_orman.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add points column to user table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN points INTEGER DEFAULT 0")
        print("Added 'points' column to user table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'points' column already exists")
        else:
            print(f"Error adding points column: {e}")

    conn.commit()
    conn.close()

    # Now create any new tables
    db.create_all()
    print("Database migration completed successfully!")
