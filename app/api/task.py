from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Task, TaskResponse,UserInput
from app.services.calendar_service import add_task_to_calendar, create_event
from app.services.task_service import add_task_to_db, get_top_task_from_db
from app.services.llm_service import generate_task_plan_wrapper
from pydantic import BaseModel

router = APIRouter()

# class TaskInput(BaseModel):
#     user_input: str
@router.post("/add-task/", response_model=TaskResponse)
async def add_task(user_input:UserInput ,db: Session = Depends(get_db)):
    print("Received user input:", user_input)
    task=generate_task_plan_wrapper(user_input)

    
    # create_event(start_time, end_time, description, title, calendar_id="primary")
    return add_task_to_db(db, task)

# @router.post("/add-task/", response_model=str)
# async def add_task(user_input:UserInput ,db: Session = Depends(get_db)):
#     task=generate_task_plan_wrapper(user_input)
#     print("//////////////////////////////////////////////////////////////////////////////////////////")
#     print("task",task.priority)
#     print("//////////////////////////////////////////////////////////////////////////////////////////")
#     print("chunks",task.chunks)
#     print("//////////////////////////////////////////////////////////////////////////////////////////")
#     print("deadline",task.deadline)
#     print("//////////////////////////////////////////////////////////////////////////////////////////")
#     print("type",task.type)
#     task = "task"
#     return task
# @router.post("/add-task", response_model=str)
# async def add_task(user_input:TaskInput ,db: Session = Depends(get_db)):
#     # task=generate_task_plan_wrapper(user_input)
#     task = "task"
#     print("user_input",user_input)
#     # return add_task_to_db(db, task)

#     return task

@router.get("/top/", response_model=TaskResponse)
async def get_top_task(db: Session = Depends(get_db)):
    task = get_top_task_from_db(db)
    if not task:
        raise HTTPException(status_code=404, detail="No tasks found")
    return task
