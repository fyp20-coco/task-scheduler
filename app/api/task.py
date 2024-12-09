from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Task, TaskResponse
from app.services.task_service import add_task_to_db, get_top_task_from_db

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def add_task(task: Task, db: Session = Depends(get_db)):
    return add_task_to_db(db, task)

@router.get("/top/", response_model=TaskResponse)
async def get_top_task(db: Session = Depends(get_db)):
    task = get_top_task_from_db(db)
    if not task:
        raise HTTPException(status_code=404, detail="No tasks found")
    return task
