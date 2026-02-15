from flask import request, jsonify
from app.services.auth_service import AuthService

class AuthController:

    @staticmethod
    def register():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "email and password required"}), 400

        try:
            AuthService.register(email, password)
            return jsonify({"message": "registered"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 409

    @staticmethod
    def login():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        try:
            token = AuthService.login(email, password)
            return jsonify({"access_token": token})
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
