import sqlite3
from pathlib import Path



def init_db():
    Path("instance").mkdir(exist_ok=True)
    db_path = Path("instance") / "database.db"
    schema = Path("schema.sql").read_text(encoding="utf-8")
    
    connection = sqlite3.connect(db_path)
    
    try:
        connection.executescript(schema)
    finally:
        #Close the connection even if SQL execution fails.
        connection.close()
        
    print("Database initialized successfully.")
    
if __name__ == "__main__":
    init_db()