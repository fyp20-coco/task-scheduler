from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# # Database configuration
# DATABASE_URL = "mysql+pymysql://root:@localhost:3306/task_db"

# Base model for SQLAlchemy
Base = declarative_base()

# Database engine
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
