from typing import List, Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime

# CHUNK MODEL
class Chunk(BaseModel):
    index: int
    title: str  # Added `title` to match `ChunkDB`
    description: str

    class Config:
        from_attributes = True  # Ensures compatibility with ORM


# TASK MODEL
class Task(BaseModel):
    priority: str  # Should match Enum("HIGH", "MEDIUM", "LOW")
    deadline: datetime
    created_at: Optional[datetime] = None  # Matches TaskDB
    chunks: List[Chunk]

    class Config:
        from_attributes = True

# CHUNK INDICES MODEL (For bulk updates)
class ChunkIndices(BaseModel):
    chunk_indices: List[int]


# TASK RESPONSE MODEL
class TaskResponse(BaseModel):
    id: int
    priority: str
    deadline: datetime  # Changed to `datetime` to match DB
    created_at: datetime
    chunks: List[Chunk]

    class Config:
        from_attributes = True


# USER CREATION MODEL
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    occupation: str
    work_start_time: str  # Kept as string (Assuming formatted times)
    work_end_time: str
    imageUrl: Optional[str] = None
    phone: Optional[str] = None

    

# AUTH TOKEN RESPONSE MODEL
class Token(BaseModel):
    access_token: str
    token_type: str
