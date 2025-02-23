from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app.models.db_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy database
fake_users_db = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[dict]:
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user and verify_password(password, existing_user.password):
        return existing_user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, name: str, password: str, occupation: str, work_start_time: str, work_end_time: str, imageUrl: str | None, phone: str | None):
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        password=hashed_password,
        name=name,
        occupation=occupation,
        work_start_time=work_start_time,
        work_end_time=work_end_time,
        imageUrl=imageUrl,
        phone=phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

