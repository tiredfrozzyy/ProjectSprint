from app.services.user_service import UserService
from flask_jwt_extended import create_access_token

class AuthService:

    @staticmethod
    def register(email: str, password: str):
        if UserService.get_by_email(email):
            raise ValueError("User already exists")

        user = UserService.create_user(email, password)
        return user

    @staticmethod
    def login(email: str, password: str):
        user = UserService.get_by_email(email)

        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")

        token = create_access_token(identity=user.id)
        return token
