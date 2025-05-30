from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Event(BaseModel):
    start_time: datetime
    end_time: datetime

    
