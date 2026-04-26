import json
import os
from collections import defaultdict
from datetime import datetime

from models import db, User, Project, Task, ProjectFile, WorkLog

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from filetype import guess
from dotenv import load_dotenv
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Функция проверки безопасного расширения файла
def allowed_file(filepath):
    kind = guess(filepath)
    if kind is None:
        return False
    # Проверяем, что это реально картинка или документ
    return kind.mime.startswith('image/') or kind.mime == 'application/pdf'


# ==================================================================
#                            1 Задание
# ==================================================================

# ==========================================
# ПОЛУЧЕНИЕ НАСТРОЕК (Делает Артур)
# ==========================================
@app.route('/api/settings', methods=['GET'])
def get_settings():
    user = db.session.execute(db.select(User)).scalar()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "notifications": {
            "messages": user.messages,
            "news": user.news,
            "tasks": user.tasks_notify,  # ИСПРАВЛЕНО: было user.tasks
            "comments": user.comments,
            "deadlines": user.deadlines
        }
    }), 200


# ==========================================
# ОБНОВЛЕНИЕ АККАУНТА (Делает Артур)
# ==========================================
@app.route('/api/settings/account', methods=['PATCH'])
def update_account():
    user = db.session.execute(db.select(User)).scalar()
    data = request.json

    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.password = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({"message": "Account updated successfully"}), 200


# ==========================================
# ЗАГРУЗКА ФОТО (Делает Татьяна)
# ==========================================
@app.route('/api/settings/avatar', methods=['POST'])
def upload_avatar():
    user = db.session.execute(db.select(User)).scalar()

    if 'avatar' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(str(file.filename))
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # ИСПРАВЛЕНО: Удаляем старый аватар, чтобы не засорять диск
        if user.avatar:
            old_filepath = user.avatar.lstrip('/')  # убираем первый слеш
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        file.save(filepath)
        user.avatar = f"/{filepath}"
        db.session.commit()

        return jsonify({"message": "Avatar uploaded", "avatar_url": user.avatar}), 200

    return jsonify({"error": "Invalid file type"}), 400


# ==========================================
# ОБНОВЛЕНИЕ УВЕДОМЛЕНИЙ (Делает Ярослав)
# ==========================================
@app.route('/api/settings/notifications', methods=['PATCH'])
def update_notifications():
    user = db.session.execute(db.select(User)).scalar()
    data = request.json

    if 'messages' in data: user.messages = bool(data['messages'])
    if 'news' in data: user.news = bool(data['news'])
    if 'tasks' in data: user.tasks_notify = bool(data['tasks'])  # ИСПРАВЛЕНО: tasks_notify
    if 'comments' in data: user.comments = bool(data['comments'])
    if 'deadlines' in data: user.deadlines = bool(data['deadlines'])

    db.session.commit()
    return jsonify({"message": "Notifications updated"}), 200


# ==================================================================
#                               2 Задание
# ==================================================================

# ==========================================
# ПОЛУЧЕНИЕ ВСЕХ ПРОЕКТОВ (Артур)
# ==========================================
@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects]), 200


# ==========================================
# СОЗДАНИЕ ПРОЕКТА (Татьяна)
# ==========================================
@app.route('/api/projects', methods=['POST'])
def create_project():
    new_project = Project(
        name=request.form.get('name'),
        goal=request.form.get('goal'),
        relevance=request.form.get('relevance'),
        problem=request.form.get('problem'),
        team_lead_id=request.form.get('team_lead_id')
    )

    # ИСПРАВЛЕНО: Безопасный парсинг дат
    try:
        if request.form.get('start_date'):
            new_project.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        if request.form.get('end_date'):
            new_project.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    db.session.add(new_project)
    db.session.flush()

    # ИСПРАВЛЕНО: Безопасный парсинг JSON
    try:
        if request.form.get('participants'):
            user_ids = json.loads(request.form.get('participants'))
            users = User.query.filter(User.id.in_(user_ids)).all()
            new_project.participants.extend(users)

        if request.form.get('tasks'):
            tasks_data = json.loads(request.form.get('tasks'))
            for t in tasks_data:
                task = Task(project_id=new_project.id, title=t['title'], progress=t.get('progress', 0))
                db.session.add(task)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in participants or tasks"}), 400

    # Сохраняем файлы с проверкой расширения
    files = request.files.getlist('files')
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            db.session.add(ProjectFile(project_id=new_project.id, filepath=f"/{filepath}"))

    db.session.commit()
    return jsonify(new_project.to_dict()), 201


# ==========================================
# РЕДАКТИРОВАНИЕ ПРОЕКТА (Ярослав)
# ==========================================
@app.route('/api/projects/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if 'name' in request.form: project.name = request.form.get('name')
    if 'goal' in request.form: project.goal = request.form.get('goal')
    if 'relevance' in request.form: project.relevance = request.form.get('relevance')
    if 'problem' in request.form: project.problem = request.form.get('problem')
    if 'status' in request.form: project.status = request.form.get('status')
    if 'team_lead_id' in request.form: project.team_lead_id = request.form.get('team_lead_id')

    try:
        if 'start_date' in request.form:
            project.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        if 'end_date' in request.form:
            project.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        if 'participants' in request.form:
            user_ids = json.loads(request.form.get('participants'))
            users = User.query.filter(User.id.in_(user_ids)).all()
            project.participants = users
    except (ValueError, json.JSONDecodeError):
        return jsonify({"error": "Invalid data format (Date or JSON)"}), 400

    files = request.files.getlist('files')
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            db.session.add(ProjectFile(project_id=project.id, filepath=f"/{filepath}"))

    db.session.commit()
    return jsonify(project.to_dict()), 200


# ==================================================================
#                               3 Задание
# ==================================================================

# ==========================================
# ОБЩАЯ СТАТИСТИКА (Артур)
# ==========================================
@app.route('/api/statistics/general', methods=['GET'])
def stats_general():
    tasks = Task.query.all()
    logs = WorkLog.query.all()

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'Завершено'])

    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    total_hours = sum(log.hours for log in logs)

    distribution = {
        "planned": len([t for t in tasks if t.status == 'В планах']),
        "in_progress": len([t for t in tasks if t.status == 'В процессе']),
        "completed": completed_tasks
    }

    return jsonify({
        "total_hours": total_hours,
        "total_tasks": total_tasks,
        "completion_rate": completion_rate,
        "distribution": distribution
    }), 200


# ==========================================
# ЭФФЕКТИВНОСТЬ КОМАНДЫ (Татьяна)
# ==========================================
@app.route('/api/statistics/team', methods=['GET'])
def stats_team():
    # ИСПРАВЛЕНО: Оптимизация запросов (избавление от N+1)
    # Делаем всего 3 запроса к БД вместо сотен
    users = User.query.all()
    completed_tasks = Task.query.filter_by(status='Завершено').all()
    all_logs = WorkLog.query.all()

    total_completed_count = len(completed_tasks)

    # Группируем задачи по пользователям
    tasks_by_user = defaultdict(int)
    for task in completed_tasks:
        if task.assignee_id:
            tasks_by_user[task.assignee_id] += 1

    # Группируем часы по пользователям
    hours_by_user = defaultdict(float)
    for log in all_logs:
        if log.user_id:
            hours_by_user[log.user_id] += log.hours

    team_stats = []
    for user in users:
        user_completed = tasks_by_user.get(user.id, 0)
        user_hours = hours_by_user.get(user.id, 0.0)

        contribution = round((user_completed / total_completed_count * 100), 1) if total_completed_count > 0 else 0

        team_stats.append({
            "user": {
                "fio": user.fio,
                "avatar": user.avatar,
                "department": user.department,
                "role": user.role
            },
            "completed_tasks": user_completed,
            "hours_worked": user_hours,
            "contribution_percent": contribution
        })

    return jsonify(team_stats), 200


# ==========================================
# Графики и Динамика (Ярослав)
# ==========================================
@app.route('/api/statistics/charts', methods=['GET'])
def stats_charts():
    logs = WorkLog.query.all()
    hours_by_date = defaultdict(float)
    for log in logs:
        date_str = log.date.isoformat() if log.date else "unknown"
        hours_by_date[date_str] += log.hours

    tasks = Task.query.all()
    tasks_by_date = defaultdict(int)
    for task in tasks:
        date_str = task.created_at.isoformat() if task.created_at else "unknown"
        tasks_by_date[date_str] += 1

    return jsonify({
        "hours_by_date": dict(hours_by_date),
        "tasks_activity_by_date": dict(tasks_by_date)
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.execute(db.select(User)).scalar():
            user = User(email="test@mail.com", phone="123456789")
            db.session.add(user)
            db.session.commit()
    app.run(host='0.0.0.0', port=8080, debug=True)