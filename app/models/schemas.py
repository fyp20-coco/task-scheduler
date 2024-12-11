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
        orm_mode = True 

class Task(BaseModel):
    priority: str
    deadline: datetime
    chunks: List[Chunk]

class ChunkIndices(BaseModel):
    chunk_indices: List[int]

class TaskResponse(BaseModel):
    id: int
    priority: str
    deadline: str
    chunks: List[Chunk]
