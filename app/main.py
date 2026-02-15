from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database, pdf_service

# Инициализация таблиц (в реальном проекте лучше использовать Alembic миграции)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ProjectSprint Backend (PostgreSQL)")


# --- USERS ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[schemas.UserResponse])
def read_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()


# --- TASKS (KANBAN) ---
@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=List[schemas.TaskResponse])
def read_tasks(db: Session = Depends(database.get_db)):
    # Возвращает задачи с подгруженными пользователями (joinedload автоматический в lazy='select')
    return db.query(models.Task).all()


@app.put("/tasks/{task_id}/status")
def move_task(task_id: int, status: models.TaskStatus, db: Session = Depends(database.get_db)):
    """Эндпоинт для Drag-and-Drop на фронтенде"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status
    db.commit()
    return {"id": task_id, "status": status, "message": "Task moved successfully"}


# --- REPORTS ---
@app.post("/reports/generate")
def generate_report(report_data: schemas.ReportRequest, db: Session = Depends(database.get_db)):
    """Генерация PDF отчета на основе закрытых задач"""
    done_tasks = db.query(models.Task).filter(models.Task.status == models.TaskStatus.DONE).all()

    pdf_file = pdf_service.generate_weekly_pdf(
        week_num=report_data.week_number,
        done_tasks=done_tasks,
        blockers=report_data.blockers,
        plans=report_data.plans
    )

    return FileResponse(pdf_file, media_type='application/pdf', filename=pdf_file)


# --- ANALYTICS ---
@app.get("/analytics/dashboard")
def get_analytics(db: Session = Depends(database.get_db)):
    """Метрики для дашборда"""
    total = db.query(models.Task).count()
    done = db.query(models.Task).filter(models.Task.status == models.TaskStatus.DONE).count()
    in_progress = db.query(models.Task).filter(models.Task.status == models.TaskStatus.IN_PROGRESS).count()
    todo = db.query(models.Task).filter(models.Task.status == models.TaskStatus.TODO).count()

    return {
        "velocity": done,  # Кол-во закрытых задач (упрощенно)
        "distribution": {
            "todo": todo,
            "in_progress": in_progress,
            "done": done
        },
        "completion_rate": f"{round((done / total) * 100, 1)}%" if total > 0 else "0%"
    }