from typing import List, Optional
from pydantic import BaseModel,EmailStr, validator
from datetime import datetime,time,timedelta
from enum import Enum
import re

class TaskType(str, Enum):
    WORK = "WORK"
    HOME = "HOME"
    HOBBY = "HOBBY"  

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Chunk(BaseModel):
    title: str
    description: str
    time_estimation: timedelta  # Use timedelta to store the time difference

    @validator("time_estimation", pre=True)
    def parse_time_estimation(cls, value):
        """Convert '30 minutes', '2 hours', '5 days', 'HH:MM-HH:MM', or 'HH:MM' into `timedelta`."""
        if isinstance(value, timedelta):  # Already a valid timedelta
            return value

        # Check if the input is a time range like '09:30-15:30' or '09:30 - 15:30' (with space)
        time_range_match = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*-\s*(\d{1,2}):(\d{2})\s*(AM|PM)", value, re.IGNORECASE)
        if time_range_match:
            # Extract start and end times and AM/PM indicators
            start_hour = int(time_range_match.group(1))
            start_minute = int(time_range_match.group(2))
            start_ampm = time_range_match.group(3).upper()
            end_hour = int(time_range_match.group(4))
            end_minute = int(time_range_match.group(5))
            end_ampm = time_range_match.group(6).upper()

            # Convert AM/PM to 24-hour format
            start_hour = cls.convert_to_24_hour(start_hour, start_ampm)
            end_hour = cls.convert_to_24_hour(end_hour, end_ampm)

            # Convert times to datetime objects
            start_time = datetime(2000, 1, 1, start_hour, start_minute)
            end_time = datetime(2000, 1, 1, end_hour, end_minute)

            # Check if end time is earlier than start time (handles crossing midnight)
            if end_time < start_time:
                # Add 24 hours to the end time to account for crossing midnight
                end_time += timedelta(days=1)

            # Calculate the time difference (timedelta)
            time_diff = end_time - start_time
            return time_diff

        # Check if the input is a standard time like 'X minutes', 'Y hours', or 'Z days'
        match = re.match(r"(\d+)\s*(minute|hour|day|minutes|hours|days)", value.lower())
        if match:
            num = int(match.group(1))
            unit = match.group(2)

            if "day" in unit:
                return timedelta(hours=num * 24)  # Convert days to hours
            elif "hour" in unit:
                return timedelta(hours=num)
            else:
                return timedelta(minutes=num)

        # Handle time format 'HH:MM' (single time without range)
        time_match = re.match(r"(\d{1,2}):(\d{2})", value)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            return timedelta(hours=hours, minutes=minutes)

        raise ValueError("Invalid time format. Expected 'X minutes', 'Y hours', 'Z days', 'HH:MM-HH:MM', or 'HH:MM'.")

    @staticmethod
    def convert_to_24_hour(hour: int, ampm: str) -> int:
        """Convert 12-hour time to 24-hour time."""
        if ampm == "AM" and hour == 12:
            return 0  # 12 AM is 00:00 in 24-hour format
        elif ampm == "PM" and hour != 12:
            return hour + 12  # PM times, except for 12 PM, add 12 to convert to 24-hour format
        return hour  # For times already in 24-hour format, return the same

    def __hash__(self):
        return hash(self.id)  # Use id for hashing

    def __eq__(self, other):
        if not isinstance(other, Chunk):
            return False
        return self.id == other.id
    class Config:
        from_attributes = True  # Ensures compatibility with ORM
# TASK MODEL
class Task(BaseModel):
    id: Optional [int]
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
    

