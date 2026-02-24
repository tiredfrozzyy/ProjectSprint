from projects_tasks.app.app import app_tasks


def start():
    app_tasks.run(debug=True)