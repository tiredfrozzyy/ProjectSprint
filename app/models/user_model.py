from app.extensions import db
from passlib.hash import argon2

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str):
        self.password_hash = argon2.hash(password)

    def check_password(self, password: str):
        return argon2.verify(password, self.password_hash)
