from fastapi import FastAPI
from app.api import auth, calendar,events,chunk,task,user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix='/api/auth', tags=['Auth'])
# app.include_router(events.router, prefix='/calendar', tags=['Calendar Events'])
app.include_router(chunk.router, prefix='/api/chunks', tags=['Chunks'])
app.include_router(task.router, prefix='/api/tasks', tags=['Tasks'])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(user.router, prefix="/api/user", tags=["User"])


