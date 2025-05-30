from fastapi import Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.newsched import get_scheduled_chunks
from app.models.db_models import ChunkDB, ScheduledChunkDB, TaskDB
from app.models.schemas import Chunk, Priority, Task, TaskType
from sqlalchemy.sql import case
from datetime import datetime,timedelta

from app.services.calendar_service import add_task_to_calendar

def timedelta_to_str(tdelta: timedelta) -> str:
    total_seconds = int(tdelta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"  # Return time as 'HH:MM' format



def add_task_to_db(db: Session, task: Task):
    """ Adds a new task with chunks to the database. """
    try:
        # Create new task
        new_task = TaskDB(priority=task.priority, deadline=task.deadline, type=task.type)
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

            estimated_time = timedelta_to_str(chunk.time_estimation)

        
            new_chunk = ChunkDB(
                task_id=new_task.id,
                chunk_index=last_index,
                title=chunk.title,
                description=chunk.description,
                time_estimation=estimated_time,
               
            )
            new_chunks.append(new_chunk)

        db.bulk_save_objects(new_chunks)  # Efficient batch insert
        db.commit()

        
        data={
            "id": new_task.id,
            "priority": new_task.priority,
            "type": new_task.type,
            "deadline": new_task.deadline.isoformat(),
            "created_at": new_task.created_at.isoformat(),  
            "chunks": [
                {
                    "index": chunk.chunk_index,
                    "title": chunk.title,
                    "description": chunk.description,
                    "time_estimation": estimated_time,
                }
                for chunk in new_chunks
            ]
        }
        start=datetime.utcnow()
        end=new_task.deadline.isoformat()
        
        get_scheduled_chunks(db,start,end)
        


        # add_task_to_calendar(data, calendar_id="primary")


        # Convert to Pydantic response model
        return data

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# def create_tasks_and_chunks_from_db_data(data: dict):
#     """Create tasks and chunks arrays from add_task_to_db data in plain Python format."""
#     tasks = []
#     chunks = []
    
#     # Create Chunk objects for the Task
#     chunk_objects = [
#         Chunk(
#             id=0,  # Placeholder; ideally, fetch from DB
#             task_id=data["id"],
#             chunk_index=chunk_data["index"],  # Use "index" instead of "chunk_index"
#             description=chunk_data["description"],
#             title=chunk_data["title"],
#             time=chunk_data["time_estimation"]
#         )
#         for chunk_data in data["chunks"]
#     ]
    
#     # Create Task object
#     task = Task(
#         id=data["id"],
#         priority=data["priority"],
#         deadline=datetime.fromisoformat(data["deadline"]),
#         created_at=datetime.fromisoformat(data["created_at"]),
#         user_id=1,  # Consider passing dynamically
#         type=data["type"],  # Use "type" to match Task model
#         chunks=chunk_objects  # Include chunks for Task model
#     )
#     tasks.append(task)
    
#     # Add chunks to separate chunks list
#     chunks.extend(chunk_objects)
    
#     return tasks, chunks  


def get_top_task_from_db(db: Session):
    """ Fetches the top-priority task with a deadline that is not in the past. """
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

        # Get the current time to compare deadlines
        current_time = datetime.utcnow()

        task = (
            db.query(TaskDB)
            .filter(TaskDB.deadline >= current_time)  # Ensure the task's deadline is not in the past
            .order_by(priority_order, TaskDB.deadline, TaskDB.created_at)
            .first()
        )
        
        if not task:
            raise HTTPException(status_code=404, detail="No tasks found")
        return {
            "id": task.id,
            "priority": task.priority,
            "type": task.type,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "chunks": [
                {
                    "index": chunk.chunk_index,
                    "title": chunk.title,
                    "description": chunk.description,
                    "estimated_time": chunk.time_estimation,
                }
                for chunk in task.chunks
            ]
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_all_tasks_from_db(db: Session):
    """ Fetches all tasks from the database. """
    try:
        tasks = db.query(TaskDB).all()
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found")

        return [
            {
                "id": task.id,
                "priority": task.priority,
                "type": task.type,
                "deadline": task.deadline.isoformat(),
                "created_at": task.created_at.isoformat(),
                "chunks": [
                    {
                        "index": chunk.chunk_index,
                        "title": chunk.title,
                        "description": chunk.description,
                        "estimated_time": chunk.time_estimation,
                    }
                    for chunk in task.chunks
                ]
            }
            for task in tasks
        ]

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_scheduled_chunks_from_db(db: Session):
    """ Fetches all scheduled chunks from the database. """
    try:
        chunks = db.query(ScheduledChunkDB).all()
        if not chunks:
            return []

        return [
            {
                "id": chunk.event_id,
                "chunk_id": chunk.chunk_id,
                "start time": chunk.start_time.isoformat(),
                "end time": chunk.end_time.isoformat(),
               
            }
            for chunk in chunks
        ]

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 

