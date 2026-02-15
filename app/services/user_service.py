from app.models.user_model import User
from app.extensions import db

class UserService:

    @staticmethod
    def get_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(email: str, password: str):
        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user
