import oci
from datetime import datetime

# Configure Oracle Gen AI client
config = oci.config.from_file()  # Load config from ~/.oci/config
ai_client = oci.ai_generative_text.models_client.ModelsClient(config)

# Define dynamic text
today = datetime.now().strftime("%Y-%m-%d")
text = """Your dynamic event description here."""

# Create payload for Oracle Gen AI
payload = {
    "parameters": {
        "temperature": 1.0,
        "maxTokens": 2048,
        "topP": 1.0,
        "frequencyPenalty": 0.0,
        "presencePenalty": 0.0,
    },
    "prompt": (
        f"Today is {today}. Use today as the starting date for task scheduling. "
        "Analyze the following description and identify actionable tasks. "
        "Provide a chunk breakdown for each task with start times, end times, "
        "summaries, and detailed descriptions. Return the output in the JSON format below:\n\n"
        f"Description: \"{text}\"\nDeadline: 2025-01-01T23:59:59Z\nPriority: HIGH\n\n"
        "Output format:\n{\n"
        "  \"priority\": \"HIGH\",\n"
        "  \"deadline\": \"2025-01-01T23:59:59Z\",\n"
        "  \"chunks\": [\n"
        "    {\n"
        "      \"index\": 1,\n"
        "      \"summary\": \"Short task summary\",\n"
        "      \"description\": \"Detailed task description\",\n"
        "      \"start_time\": \"YYYY-MM-DDTHH:MM:SSZ\",\n"
        "      \"end_time\": \"YYYY-MM-DDTHH:MM:SSZ\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n}\n\n"
        "Rules for JSON generation:\n"
        "- Create 2-15 logical task chunks.\n"
        "- Include clear, actionable summaries and detailed descriptions for each task.\n"
        "- Distribute tasks logically before the deadline.\n"
        "- Avoid creating tasks that span days; tasks should only last a few hours at most.\n"
        "- Estimate realistic time allocations and avoid wide time gaps."
    ),
}

# Call Oracle Gen AI
response = ai_client.generate_text(model_id="ocid1.model.oc1..your_model_ocid", generate_text_details=payload)

# Process response
output = response.data.text
print(output)
