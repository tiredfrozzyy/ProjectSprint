from flask import Blueprint, jsonify
from projects_competencies.models.models import SkillProgress

skills_bp = Blueprint("skills", __name__)

@skills_bp.route("/user/<int:user_id>")
def get_user_skills(user_id):
    skills = SkillProgress.query.filter_by(user_id=user_id).all()
    result = []
    for s in skills:
        result.append({
            "skill_id": s.skill_id,
            "progress": s.progress
        })
    return jsonify(result)
