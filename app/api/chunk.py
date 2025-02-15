from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Chunk, ChunkIndices
from app.services.chunk_service import add_chunks_to_task, delete_chunks

router = APIRouter()

@router.post("/{task_id}")
async def add_chunks(task_id: int, chunks: list[Chunk], db: Session = Depends(get_db)):
    return add_chunks_to_task(db, task_id, chunks)

@router.delete("/{task_id}")
async def remove_chunks(task_id: int, chunk_indices: ChunkIndices, db: Session = Depends(get_db)):
    return delete_chunks(db, task_id, chunk_indices)
