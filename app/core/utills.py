from pydantic import ValidationError
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.db_models import ChunkDB, ScheduledChunkDB, TaskDB
from app.models.schemas import Chunk, Priority, Task, TaskType
from datetime import datetime, timedelta, time

def get_chunks_and_tasks_with_scheduled_chunks(db: Session):
    # Fetch all tasks
    db_tasks = db.query(TaskDB).all()
    
    # Fetch all chunks, including those without scheduled chunks
    stmt = (
        select(ChunkDB, TaskDB)
        .join(TaskDB, TaskDB.id == ChunkDB.task_id)
        .outerjoin(ScheduledChunkDB, ScheduledChunkDB.chunk_id == ChunkDB.id)
    )
    result = db.execute(stmt).all()
    
    tasks = []
    chunks = []
    task_dict = {}
    print("Fetched tasks and chunks from the database.")
    for chunk_db, task_db in result:
        # Convert time_estimation to timedelta
        if isinstance(chunk_db.time_estimation, time):
            # Convert time object to timedelta
            time_estimation = timedelta(
                hours=chunk_db.time_estimation.hour,
                minutes=chunk_db.time_estimation.minute,
                seconds=chunk_db.time_estimation.second
            )
        elif isinstance(chunk_db.time_estimation, datetime):
            # Convert datetime object to timedelta
            time_estimation = timedelta(
                hours=chunk_db.time_estimation.hour,
                minutes=chunk_db.time_estimation.minute,
                seconds=chunk_db.time_estimation.second
            )
        else:
            # Assume time_estimation is a string like "30 minutes" or parse as needed
            time_estimation = chunk_db.time_estimation  # Validator will handle parsing
        
        print(f"Processing chunk {chunk_db.id} for task {task_db.id} with time estimation: {time_estimation}")
        try:
            chunk = Chunk(
                id=chunk_db.id,
                task_id=chunk_db.task_id,
                chunk_index=chunk_db.chunk_index,
                description=chunk_db.description,
                title=chunk_db.title,
                time_estimation=time_estimation
            )
            chunks.append(chunk)
            
            if task_db.id not in task_dict:
                task_dict[task_db.id] = {
                    "id": task_db.id,
                    "priority": Priority(task_db.priority),
                    "deadline": task_db.deadline,
                    "created_at": task_db.created_at,
                    "user_id": task_db.user_id,
                    "type": TaskType(task_db.type),
                    "chunks": []
                }
            task_dict[task_db.id]["chunks"].append(chunk)
        except ValidationError as e:
            print(f"Validation error for chunk {chunk_db.id}: {e}")
            continue
    
    # Add tasks without chunks
    for db_task in db_tasks:
        if db_task.id not in task_dict:
            task_dict[db_task.id] = {
                "id": db_task.id,
                "priority": Priority(db_task.priority),
                "deadline": db_task.deadline,
                "created_at": db_task.created_at,
                "user_id": db_task.user_id,
                "type": TaskType(db_task.type),
                "chunks": []
            }
    
    tasks = [Task(**task_data) for task_data in task_dict.values()]
    return tasks, chunks

def get_last_task_with_chunks(db_session: Session):
    try:
        # Query the last task ordered by created_at
        last_task_db = (
            db_session.query(TaskDB)
            .order_by(desc(TaskDB.created_at))
            .first()
        )
        
        if not last_task_db:
            return [], []  # Return empty lists instead of None
          # Convert chunks
        chunks = []
        for chunk_db in last_task_db.chunks:
            # Convert time_estimation to timedelta
            if isinstance(chunk_db.time_estimation, time):
                # Convert time object to timedelta
                time_estimation = timedelta(
                    hours=chunk_db.time_estimation.hour,
                    minutes=chunk_db.time_estimation.minute,
                    seconds=chunk_db.time_estimation.second
                )
            elif isinstance(chunk_db.time_estimation, datetime):
                # Convert datetime object to timedelta
                time_estimation = timedelta(
                    hours=chunk_db.time_estimation.hour,
                    minutes=chunk_db.time_estimation.minute,
                    seconds=chunk_db.time_estimation.second
                )
            else:
                time_estimation = chunk_db.time_estimation  # Validator will parse
            
            try:
                chunk = Chunk(
                    id=chunk_db.id,
                    task_id=chunk_db.task_id,
                    chunk_index=chunk_db.chunk_index,
                    title=chunk_db.title,
                    description=chunk_db.description,
                    time_estimation=time_estimation
                )
                chunks.append(chunk)
            except ValidationError as e:
                print(f"Validation error for chunk {chunk_db.id}: {e}")
                continue
        
        # Convert task
        task = Task(
            id=last_task_db.id,
            priority=Priority(last_task_db.priority),
            deadline=last_task_db.deadline,
            created_at=last_task_db.created_at,
            user_id=last_task_db.user_id,
            type=TaskType(last_task_db.type),
            chunks=chunks
        )
        
        return [task], chunks
    
    except ValidationError as e:
        print(f"Validation error: {e}")
        return [], []
    except Exception as e:
        print(f"Error retrieving task: {e}")
        return [], []