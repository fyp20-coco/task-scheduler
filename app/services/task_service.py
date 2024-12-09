from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.db_models import ChunkDB, TaskDB
from app.models.schemas import Chunk, Task

def add_task_to_db(db: Session, task: Task):
    try:
        # Adding the task to the database
        new_task = TaskDB(priority=task.priority, deadline=task.deadline)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)  # Refresh to get the newly added task with its ID

        # Add chunks to the task
        chunk_models = []
        for chunk in task.chunks:
            new_chunk = ChunkDB(
                task_id=new_task.id,
                index=chunk.index,
                description=chunk.description,
                start_time=chunk.start_time,
                end_time=chunk.end_time,
            )
            db.add(new_chunk)
            db.commit()
            # Convert the ChunkDB instance to a Pydantic model
            chunk_models.append(Chunk.from_orm(new_chunk))  # Convert to Pydantic model

        # Prepare the response as a dictionary matching TaskResponse model
        return {
            "id": new_task.id,
            "priority": new_task.priority,
            "deadline": new_task.deadline.isoformat(),  # Convert deadline to string
            "chunks": [chunk.dict() for chunk in chunk_models]  # Use dict() on each chunk Pydantic model
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



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
