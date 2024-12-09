from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.db_models import TaskDB
from app.models.schemas import Task

def add_task_to_db(db: Session, task: Task):
    new_task = TaskDB(priority=task.priority, deadline=task.deadline)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_top_task_from_db(db: Session):
    task = (
        db.query(TaskDB)
        .order_by(TaskDB.priority, TaskDB.deadline, TaskDB.created_at)
        .first()
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="No tasks found")
    
    # Convert TaskDB object to a dictionary before returning
    return {
        "id": task.id,
        "priority": task.priority,
        "deadline": task.deadline.isoformat(),  # Ensure datetime is formatted as string
        "chunks": [
            {
                "index": chunk.index,
                "description": chunk.description,
                "start_time": chunk.start_time.isoformat(),  # Ensure datetime is formatted as string
                "end_time": chunk.end_time.isoformat()
            }
            for chunk in task.chunks
        ]
    }
