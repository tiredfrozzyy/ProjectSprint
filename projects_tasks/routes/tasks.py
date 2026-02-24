from flask import Blueprint, request, jsonify
from projects_tasks.models.models import db, Task

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "progress": t.progress,
            "column_id": t.column_id
        } for t in tasks
    ])


@task_bp.route("/", methods=["POST"])
def create_task():
    data = request.json

    task = Task(
        title=data["title"],
        description=data.get("description"),
        progress=0,
        column_id=data["column_id"]
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created"})