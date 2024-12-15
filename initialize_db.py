from app import app, db

# Create tables in the database
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
