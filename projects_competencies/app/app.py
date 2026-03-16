from flask import Flask
from config import Config
from projects_competencies.models.models import db
from projects_competencies.routes.users import users_bp
from projects_competencies.routes.skills import skills_bp
from flask_cors import CORS


app_competencies = Flask(__name__)
app_competencies.config.from_object(Config)

CORS(app_competencies)
db.init_app(app_competencies)

app_competencies.register_blueprint(users_bp, url_prefix="/users")
app_competencies.register_blueprint(skills_bp, url_prefix="/skills")
with app_competencies.app_context():
    db.create_all()