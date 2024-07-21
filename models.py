from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), unique=True, nullable=False)
    userpw = db.Column(db.String(255), nullable=False)