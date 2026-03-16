from projects_tasks.app.app import app_tasks
from projects_competencies.app.app import app_competencies


def start():
    app_tasks.run(debug=True)
