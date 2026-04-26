from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# Таблица-связка для отношения "Многие-ко-Многим" (Проекты <-> Участники)
project_participants = db.Table('project_participants',
                                db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
                                db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
                                )


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # --- Поля из Настроек ---
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255))
    avatar = db.Column(db.String(200))

    messages = db.Column(db.Boolean, default=True)
    news = db.Column(db.Boolean, default=True)
    tasks_notify = db.Column(db.Boolean, default=True) # Обратите внимание на это имя
    comments = db.Column(db.Boolean, default=True)
    deadlines = db.Column(db.Boolean, default=True)

    # --- Поля из Проектов ---
    fio = db.Column(db.String(150))
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "avatar": self.avatar,
            "fio": self.fio,
            "department": self.department,
            "role": self.role,
            "notifications": {
                "messages": self.messages,
                "news": self.news,
                "tasks": self.tasks_notify,
                "comments": self.comments,
                "deadlines": self.deadlines
            }
        }


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    title = db.Column(db.String(200))
    progress = db.Column(db.Integer, default=0)  # Процент выполнения задачи

    # 🔥 НОВЫЕ ПОЛЯ ДЛЯ СТАТИСТИКИ:
    status = db.Column(db.String(50), default='В планах')  # 'В планах', 'В процессе', 'Завершено'
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Кто делает
    created_at = db.Column(db.Date, default=date.today)

    assignee = db.relationship('User', foreign_keys=[assignee_id])
    work_logs = db.relationship('WorkLog', backref='task', lazy=True, cascade="all, delete-orphan")


class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date, default=date.today)
    hours = db.Column(db.Float, default=0.0) # Сколько часов потрачено


class ProjectFile(db.Model):
    __tablename__ = 'project_files'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    filepath = db.Column(db.String(255))


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    goal = db.Column(db.Text)
    relevance = db.Column(db.Text)
    problem = db.Column(db.Text)
    status = db.Column(db.String(50), default='В процессе')  # 'Готов' или 'В процессе'

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Связи
    team_lead_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_lead = db.relationship('User', foreign_keys=[team_lead_id])

    participants = db.relationship('User', secondary=project_participants, lazy='subquery')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade="all, delete-orphan")
    files = db.relationship('ProjectFile', backref='project', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        # 1. Считаем дни до конца
        days_left = (self.end_date - date.today()).days if self.end_date else 0

        # 2. Считаем процент выполнения проекта
        if self.status == 'Готов':
            project_progress = 100
        else:
            if self.tasks:
                total_progress = sum(task.progress for task in self.tasks)
                project_progress = round(total_progress / len(self.tasks))
            else:
                project_progress = 0

        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "goal": self.goal,
            "relevance": self.relevance,
            "problem": self.problem,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "days_left": max(0, days_left),  # Чтобы не было минусовых дней
            "project_progress": project_progress,

            "team_lead": {"id": self.team_lead.id, "fio": self.team_lead.fio} if self.team_lead else None,

            "participants_count": len(self.participants),
            "participants": [{
                "id": p.id, "fio": p.fio, "department": p.department,
                "role": p.role, "avatar": p.avatar
            } for p in self.participants],

            "tasks": [{"id": t.id, "title": t.title, "progress": t.progress} for t in self.tasks],
            "files": [{"id": f.id, "filepath": f.filepath} for f in self.files]
        }