from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///site.db"  # Modify if your path is different

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("UPDATE room SET type='SINGLE' WHERE type='Single'"))
    conn.execute(text("UPDATE room SET type='DOUBLE' WHERE type='Double'"))

print("Database updated successfully!")
