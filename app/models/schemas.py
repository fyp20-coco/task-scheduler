from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Chunk(BaseModel):
    index: Optional[int]
    description: str
    start_time: datetime
    end_time: datetime
    summary: str

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility

class Task(BaseModel):
    priority: str
    deadline: datetime
    chunks: List[Chunk]

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility

class ChunkIndices(BaseModel):
    chunk_indices: List[int]

class TaskResponse(BaseModel):
    id: int
    priority: str
    deadline: str  # Keep this as string since the ORM model likely provides `datetime`
    chunks: List[Chunk]

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility
