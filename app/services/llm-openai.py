from openai import OpenAI
from datetime import datetime

api_key = "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"

client = OpenAI(api_key=api_key)

# Dynamic variables
today = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
role_context = "You are a project management assistant specializing in task breakdown and scheduling."
text = """The cricket match marketing committee has an exciting lineup of tasks to ensure a successful event on January 1, 2025. First, the logo and theme need to be finalized, and the page logo and cover should be updated. Announcements will follow for the event, logo, and T-shirts, along with opening registrations. Posts will keep the audience engaged, including reminders about the T-shirt preorder deadline, registration updates, and partnership announcements for title, gold, silver, and bronze sponsors. Flyers and banners will highlight sponsors and deadlines. Teams will be announced, along with details about tournament awards, gift partners, and sub-events. A countdown will build excitement as the match day approaches, with posts on key milestones like “2 days more,” “1 day more,” and “Happening Today.” After the event, the committee will share highlights, including runners-up, champions, best performers, and a thank-you message to students. The after-video and a photo album will wrap up the campaign, showcasing the event’s success and engaging the community with memorable moments."""

# OpenAI Chat API request
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": role_context
        },
        {
            "role": "user",
            "content": (
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
            )
        },
        {
            "role": "assistant",
            "content": (
                "Output format and rules are included for clarity. Please ensure the JSON "
                "follows the specified structure and adheres to all outlined rules."
            )
        }
    ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)


message = response.choices[0].message
print(message.content)