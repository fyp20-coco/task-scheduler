from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"  # Renamed table to plural form for consistency

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    occupation = Column(String(255), nullable=False)
    work_start_time = Column(String(255), nullable=False)
    work_end_time = Column(String(255), nullable=False)
    imageUrl = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # When a user is deleted, all related tasks should also be deleted.
    tasks = relationship("TaskDB", back_populates="user", cascade="all, delete", passive_deletes=True)


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Enum("HIGH", "MEDIUM", "LOW", name="priority_enum"), nullable=False)
    type = Column(Enum("WORK", "HOME","HOBBY", name="task_type_enum"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Foreign key to User model
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  
    user = relationship("User", back_populates="tasks")

    # Relationship to chunks (A task should only be deleted if it has no chunks left)
    chunks = relationship("ChunkDB", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)


class ChunkDB(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)  
    chunk_index = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)  # Changed from String to Text for long descriptions

    task = relationship("TaskDB", back_populates="chunks")

