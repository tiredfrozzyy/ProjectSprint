from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import TaskStatus


# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: str
    skills: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    assignee_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    assignee: Optional[UserResponse] = None  # Вложенный объект пользователя

    class Config:
        orm_mode = True


# --- Report Schema ---
class ReportRequest(BaseModel):
    week_number: int
    blockers: str
    plans: str