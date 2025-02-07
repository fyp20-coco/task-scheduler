from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
# from app.services.user_service import create_user, get_user_by_email
# from app.services.event_service import create_event, get_events
from app.models.db_models import User

router = APIRouter()

# @router.post("/signup")
# def signup(email: str, password: str, name: str, db: Session = Depends(get_db)):
#     if get_user_by_email(db, email):
#         raise HTTPException(status_code=400, detail="User already exists")
#     return create_user(db, email, password, name)

# @router.post("/create_event")
# def create_new_event(event_data: dict, db: Session = Depends(get_db)):
#     return create_event(db, event_data)

# @router.get("/getevents")
# def get_all_events(db: Session = Depends(get_db)):
#     return get_events(db)

@router.get("/signup/moredetails")
def signup_more_details(user_data: dict, db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="User already exists")
    user = db.query(User).filter(User.email == user_data["email"]).first()
    user.occupation = user_data["occupation"]
    user.start_time = user_data["start_time"]
    user.end_time = user_data["end_time"]
    user.image = user_data["image"]
    user.phone = user_data["phone"]
    db.commit()
    db.refresh(user)
    return user

@router.get("/getuser_details")
def get_user_details(email: str, db: Session = Depends(get_db)):
    return get_user_by_email(db, email)