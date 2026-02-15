from flask import Blueprint
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)

auth_bp.post("/register")(AuthController.register)
auth_bp.post("/login")(AuthController.login)
