from fastapi import FastAPI
from app.api import auth, calendar,events,chunk,task,user

app = FastAPI()

app.include_router(auth.router, prefix='/auth', tags=['Auth'])
# app.include_router(events.router, prefix='/calendar', tags=['Calendar Events'])
app.include_router(chunk.router, prefix='/chunks', tags=['Chunks'])
app.include_router(task.router, prefix='/tasks', tags=['Tasks'])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
app.include_router(user.router, prefix="/user", tags=["User"])


