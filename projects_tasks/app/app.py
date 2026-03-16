from flask import Flask
from config import Config
from projects_tasks.models.models import db
from projects_tasks.routes.tasks import task_bp
from projects_tasks.routes.projects import project_bp
from flask_cors import CORS

app_tasks = Flask(__name__)
app_tasks.config.from_object(Config)

CORS(app_tasks)
db.init_app(app_tasks)

app_tasks.register_blueprint(task_bp, url_prefix="/api/projects_tasks")
app_tasks.register_blueprint(project_bp, url_prefix="/api/projects")

with app_tasks.app_context():
    db.create_all()