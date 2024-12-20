from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


# Initialize Flask app and database
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/engagetrack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from app import routes, models

# Ensure database is created
with app.app_context():
    db.create_all()
