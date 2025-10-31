import sqlite3
import os

# ---------- CONFIG ----------
DB_PATH = "database/labour_db.sqlite"
SCHEMA_PATH = "database/schema.sql"
DATA_PATH = "database/data.sql"  # optional — skip if not needed


def initialize_database():
    """Create a new SQLite database using schema and data files."""
    # Ensure database folder exists
    os.makedirs("database", exist_ok=True)

    # Remove old database if you want a clean setup
    if os.path.exists(DB_PATH):
        print("Existing database found — replacing it...")
        os.remove(DB_PATH)

    # Connect to new database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Run schema.sql
    print("Applying schema...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
        conn.executescript(schema)

    # Optionally insert sample data
    if os.path.exists(DATA_PATH):
        print("Inserting sample data...")
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = f.read()
            conn.executescript(data)
    else:
        print("No data.sql found — skipping data insertion.")

    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully at: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()