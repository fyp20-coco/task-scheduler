from sqlalchemy.orm import Session
from app.models.schemas import User
from app.models.event import Event

# def create_user(db: Session, email: str, name: str, password: str,occupation: str, work_start_time: str, work_end_time: str, imageUrl: str, phone: str, created_at: Optional[str] = None) -> User):
#     hashed_password = hash_password(password)
#     new_user = User(email=email, password=password, name=name)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
