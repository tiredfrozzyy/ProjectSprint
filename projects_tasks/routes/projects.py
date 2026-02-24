from flask import Blueprint, request, jsonify
from projects_tasks.models.models import db, Project

project_bp = Blueprint("projects", __name__)


@project_bp.route("/", methods=["GET"])
def get_projects():
    projects = Project.query.all()

    return jsonify([
        {"id": p.id, "title": p.title}
        for p in projects
    ])


@project_bp.route("/", methods=["POST"])
def create_project():
    data = request.json

    project = Project(title=data["title"])

    db.session.add(project)
    db.session.commit()

    return jsonify({"message": "Project created"})
