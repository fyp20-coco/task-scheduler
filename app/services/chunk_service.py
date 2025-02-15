from sqlalchemy.orm import Session
from app.models.db_models import ChunkDB, TaskDB
from app.models.schemas import Chunk, ChunkIndices
from sqlalchemy.exc import SQLAlchemyError

def add_chunks_to_task(db: Session, task_id: int, chunks: list[Chunk]):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise ValueError("Task not found")
    
    print("Task found")
    last_chunk = db.query(ChunkDB).filter(ChunkDB.task_id == task_id).order_by(ChunkDB.chunk_index.desc()).first()
    last_index = last_chunk.chunk_index if last_chunk else 0

    for chunk in chunks:
        new_chunk = ChunkDB(
            task_id=task_id,
            chunk_index=last_index + 1,
            title=chunk.title,
            description=chunk.description,
        )
        db.add(new_chunk)
        last_index += 1
    db.commit()
    return {"message": "Chunks added successfully"}

def delete_chunks(db: Session, task_id: int, chunk_indices: ChunkIndices):
    """ Deletes specified chunks and removes the task if no chunks remain. """
    try:
        # Find chunks to delete
        chunks = db.query(ChunkDB).filter(
            ChunkDB.task_id == task_id,
            ChunkDB.chunk_index.in_(chunk_indices.chunk_indices)
        ).all()

        if not chunks:
            return {"message": "No matching chunks found for deletion"}

        # Delete selected chunks
        for chunk in chunks:
            db.delete(chunk)
        db.commit()  # Commit after deleting chunks

        # Check if the task has remaining chunks
        remaining_chunks = db.query(ChunkDB).filter(ChunkDB.task_id == task_id).count()
        if remaining_chunks == 0:
            db.query(TaskDB).filter(TaskDB.id == task_id).delete()
            db.commit()
            return {"message": f"All chunks deleted, task {task_id} removed"}

        return {"message": f"Chunks {chunk_indices.chunk_indices} deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Error deleting chunks: {str(e)}")
