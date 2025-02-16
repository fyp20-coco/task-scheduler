from pathlib import Path
import ollama
import json
from datetime import datetime
from app.models.schemas import TaskPlanResponse,UserInput


MAX_RETRIES = 3  # Maximum number of retries for invalid JSON


def load_prompt_template() -> str:
    template_path = Path(__file__).parent.parent / 'templates' / 'task_prompt.txt'
    with open(template_path, 'r') as f:
        return f.read()


def validate_json(output: str) -> bool:
    """Validate if the output is a valid JSON and conforms to the expected structure."""
    try:
        # Attempt to parse the JSON
        parsed = json.loads(output)
        # Validate using Pydantic model (ensures structure is correct)
        TaskPlanResponse.parse_obj(parsed)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def generate_task_plan(user_input, model_name) -> dict:
    prompt_template = load_prompt_template()
    today = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    formatted_prompt = prompt_template.format(
        today=today,
        description=user_input.text,
        deadline=user_input.deadline.isoformat(),
        priority=user_input.priority,
        task_type=user_input.type
    )

    client = ollama.Client()
    retries = 0

    while retries < MAX_RETRIES:
        response = client.generate(
            model=model_name,
            prompt=formatted_prompt,
            format='json',
            options={
                'temperature': 1.0,
                'num_ctx': 2048,
            }
        )

        output = response.get('response', '')

        if validate_json(output):
            return TaskPlanResponse.parse_raw(output)  # Return valid JSON as a Python object

        print(f"Invalid JSON output. Retrying... ({retries + 1}/{MAX_RETRIES})")
        retries += 1

    raise ValueError("Failed to generate valid JSON after maximum retries.")
