from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.db_models import ChunkDB, TaskDB
from app.models.schemas import Chunk, Task
from sqlalchemy.sql import case


def add_task_to_db(db: Session, task: Task):
    """ Adds a new task with chunks to the database. """
    try:
        # Create new task
        new_task = TaskDB(priority=task.priority, deadline=task.deadline)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)  # Get task ID after commit

        # Get the last chunk index for this task (start from 0 if no chunks exist)
        last_chunk = db.query(ChunkDB).filter(ChunkDB.task_id == new_task.id).order_by(ChunkDB.chunk_index.desc()).first()
        last_index = last_chunk.chunk_index if last_chunk else 0

        # Create and store chunks
        new_chunks = []
        for chunk in task.chunks:
            last_index += 1 
        
            new_chunk = ChunkDB(
                task_id=new_task.id,
                chunk_index=last_index,
                title=chunk.title,
                description=chunk.description,
               
            )
            new_chunks.append(new_chunk)

        db.bulk_save_objects(new_chunks)  # Efficient batch insert
        db.commit()

        # Convert to Pydantic response model
        return {
            "id": new_task.id,
            "priority": new_task.priority,
            "deadline": new_task.deadline.isoformat(),
            "created_at": new_task.created_at.isoformat(),  
            "chunks": [
                {
                    "index": chunk.chunk_index,
                    "title": chunk.title,
                    "description": chunk.description,
                }
                for chunk in new_chunks
            ]
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_top_task_from_db(db: Session):
    """ Fetches the top-priority task from the database. """
    try:
        # Ensure proper ordering:
        # - High priority first
        # - Earliest deadline first
        # - Earliest created_at first (if priorities & deadlines are the same)
        priority_order = case(
        (TaskDB.priority == "HIGH", 1),
        (TaskDB.priority == "MEDIUM", 2),
        (TaskDB.priority == "LOW", 3),
        else_=4  # Default case
        )

        task = (
            db.query(TaskDB)
            .order_by(priority_order, TaskDB.deadline, TaskDB.created_at)
            .first()
        )

        if not task:
            raise HTTPException(status_code=404, detail="No tasks found")

        return {
            "id": task.id,
            "priority": task.priority,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),  
            "chunks": [
                {
                    "index": chunk.chunk_index,
                    "title": chunk.title,
                    "description": chunk.description,
                }
                for chunk in task.chunks
            ]
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
