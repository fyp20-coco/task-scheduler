from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Chunk(BaseModel):
    index: Optional[int]
    description: str
    start_time: datetime
    end_time: datetime

class Task(BaseModel):
    priority: str
    deadline: datetime
    chunks: List[Chunk]

class ChunkIndices(BaseModel):
    chunk_indices: List[int]

class TaskResponse(BaseModel):
    id: int
    priority: str
    deadline: datetime
    chunks: List[Chunk]
