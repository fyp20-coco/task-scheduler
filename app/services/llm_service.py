from app.core.ollama_client import generate_task_plan
from app.models.schemas import Task

models = [
        "deepseek-r1:1.5b",
        "qwen2.5:1.5b",
        "qwen2.5:0.5b",
        "llama3.2:1b"
    ]

def generate_task_plan_wrapper(user_input, model_name=models[1]):
    try:
        response = generate_task_plan(user_input, model_name)

        print("\nGenerated Task Plan:")
        print(response)

        new_task = Task(priority=response.priority, deadline=response.deadline, type=response.type,chunks=response.steps)

        # # Save response to database
        # save_to_db(response)
        return new_task 

    except ValueError as e:
            print(f"Error: {e}")