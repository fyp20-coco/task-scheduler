from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Enum("HIGH", "MEDIUM", "LOW", name="priority_enum"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    chunks = relationship("ChunkDB", back_populates="task", cascade="all, delete")

class ChunkDB(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    index = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    task = relationship("TaskDB", back_populates="chunks")
