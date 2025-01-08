from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi import Query
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import authenticate_user, create_access_token, add_user
from app.models.db_models import Token, User
from datetime import timedelta

router = APIRouter()



@router.post("/signup", status_code=201)
def signup(user: User):
    if not add_user(user.username, user.password):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "User created successfully"}

@router.post("/signin", response_model=Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
