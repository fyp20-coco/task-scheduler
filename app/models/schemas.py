from typing import List, Optional
from pydantic import BaseModel,EmailStr, validator
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    WORK = "WORK"
    HOME = "HOME"
    HOBBY = "HOBBY"  

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# CHUNK MODEL
class Chunk(BaseModel):
    title: str  # Added `title` to match `ChunkDB`
    description: str

    class Config:
        from_attributes = True  # Ensures compatibility with ORM


# TASK MODEL
class Task(BaseModel):
    priority: Priority  # Should match Enum("HIGH", "MEDIUM", "LOW")
    deadline: datetime
    type: TaskType 
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

class TaskStep(BaseModel):
    index: int
    title: str
    description: str
    time_estimation: str
    dependencies: list[int]


class TaskPlanResponse(BaseModel):
    priority: str
    type: str
    deadline: str
    steps: list[TaskStep]
  
class UserInput(BaseModel):
    text: str
    priority: str
    type: Optional[str] = "WORK"
    deadline: datetime

    @validator('priority')
    def validate_priority(cls, v):
        if v.upper() not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            raise ValueError('Invalid priority level')
        return v.upper()

    @validator('type')
    def validate_type(cls, v):
        if v.upper() not in ['WORK', 'HOME', 'HOBBY']:
            raise ValueError('Invalid task type')
        return v.upper()
