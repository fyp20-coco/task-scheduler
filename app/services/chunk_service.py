from sqlalchemy.orm import Session
from app.models.db_models import ChunkDB, TaskDB
from app.models.schemas import Chunk, ChunkIndices

def add_chunks_to_task(db: Session, task_id: int, chunks: list[Chunk]):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise ValueError("Task not found")
    
    last_chunk = db.query(ChunkDB).filter(ChunkDB.task_id == task_id).order_by(ChunkDB.index.desc()).first()
    last_index = last_chunk.index if last_chunk else 0

    for chunk in chunks:
        new_chunk = ChunkDB(
            task_id=task_id,
            index=last_index + 1,
            description=chunk.description,
            start_time=chunk.start_time,
            end_time=chunk.end_time,
        )
        db.add(new_chunk)
        last_index += 1
    db.commit()
    return {"message": "Chunks added successfully"}

def delete_chunks(db: Session, task_id: int, chunk_indices: ChunkIndices):
    chunks = db.query(ChunkDB).filter(ChunkDB.task_id == task_id, ChunkDB.index.in_(chunk_indices.chunk_indices)).all()
    for chunk in chunks:
        db.delete(chunk)
    db.commit()

    remaining_chunks = db.query(ChunkDB).filter(ChunkDB.task_id == task_id).all()
    if not remaining_chunks:
        db.query(TaskDB).filter(TaskDB.id == task_id).delete()
        db.commit()
        return {"message": f"All chunks and task {task_id} deleted"}
    return {"message": f"Chunks {chunk_indices.chunk_indices} deleted"}
