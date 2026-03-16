from flask import Blueprint, jsonify
from projects_competencies.models.models import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "role": user.role
        })
    return jsonify(result)
