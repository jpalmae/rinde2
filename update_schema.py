from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        with db.engine.connect() as conn:
            # Add status column
            try:
                conn.execute(text("ALTER TABLE clients ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
                print("Added status column.")
            except Exception as e:
                print(f"Could not add status column (might already exist): {e}")

            # Add created_by column
            try:
                conn.execute(text("ALTER TABLE clients ADD COLUMN created_by INTEGER REFERENCES users(id)"))
                print("Added created_by column.")
            except Exception as e:
                print(f"Could not add created_by column (might already exist): {e}")
            
            conn.commit()
            print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
