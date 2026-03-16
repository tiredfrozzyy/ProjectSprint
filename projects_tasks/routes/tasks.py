from flask import Blueprint, request, jsonify
from projects_tasks.models.models import db, Task

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/", methods=["POST"])
def create_task():
    data = request.json

    task = Task(
        title=data["title"],
        description=data.get("description"),
        department_name=data.get("department"),
        responsible=data.get("responsible"),
        list_participants=data.get("participants", []),
        priority=data.get("priority"),
        progress=0,
        project_id=data.get("project_id")
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created"})


@task_bp.route("/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"})
    data = request.json
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "department" in data:
        task.department = data["department"]
    if "responsible" in data:
        task.responsible = data["responsible"]
    if "participants" in data:
        task.participants = data["participants"]
    if "priority" in data:
        task.priority = data["priority"]
    if "progress" in data:
        task.progress = data["progress"]
    db.session.commit()
    return jsonify({"message": "Task updated"})



@task_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"})
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})


@task_bp.route("/", methods=["GET"])
def get_tasks():
    project_id = request.args.get("project_id")
    department = request.args.get("department")
    responsible = request.args.get("responsible")
    query = Task.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if department:
        query = query.filter_by(department=department)
    if responsible:
        query = query.filter_by(responsible=responsible)
    tasks = query.all()
    return jsonify([
        {
            "id": task.id,
            "title": task.title,
            "department": task.department,
            "responsible": task.responsible,
            "priority": task.priority,
            "progress": task.progress
        }
        for task in tasks
    ])
