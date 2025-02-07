from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Enum("HIGH", "MEDIUM", "LOW", name="priority_enum"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    # ForeignKey to User model
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False) 
    chunks = relationship("ChunkDB", back_populates="task", cascade="all, delete")
    # Corrected relationship to User model
    user = relationship("User", back_populates="tasks")

class ChunkDB(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    index = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    task = relationship("TaskDB", back_populates="chunks")
    event_id=Column(String, nullable=False)
    summary = Column(Text, nullable=False)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    occupation = Column(String(255), nullable=False)
    work_start_time = Column(String(255), nullable=False)
    work_end_time = Column(String(255), nullable=False)
    imageUrl = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    tasks = relationship("TaskDB", back_populates="user", cascade="all, delete")




