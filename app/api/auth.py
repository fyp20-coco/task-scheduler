from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi import Query
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import authenticate_user, create_access_token, add_user
from app.models.schemas import Token, UserCreate
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth import create_user, get_user_by_email
from app.models.db_models import User

router = APIRouter()


# 'password', 'occupation', '_work_start_time', and 'work_end_time'
# @router.post("/signup", status_code=201)
# def signup(user: User):
#     if not add_user(user.username,user.email, user.password,user.occupation,user.work_start_time,user.work_end_time,user.imageUrl,user.phone):
#         raise HTTPException(status_code=400, detail="User already exists")
#     return {"msg": "User created successfully"}

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    new_user = create_user(
        db=db,
        name=user.name,
        email=user.email,
        password=user.password,
        occupation=user.occupation,
        work_start_time=user.work_start_time,
        work_end_time=user.work_end_time,
        imageUrl=user.imageUrl,
        phone=user.phone
    )
    return {"message": "User created successfully", "user": new_user}



@router.post("/signin", response_model=Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
