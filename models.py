from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Nonprofit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    charity_id = db.Column(db.String(255), nullable=True)
    short_url = db.Column(db.String(255), nullable=True)
    long_url = db.Column(db.String(2048), nullable=True)
    ein = db.Column(db.String(10), nullable=False, default="00-0000000")
    qr_code = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RedirectLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nonprofit_id = db.Column(db.Integer, db.ForeignKey('nonprofit.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

