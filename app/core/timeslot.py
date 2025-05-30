from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.newsched import get_scheduled_chunks
from app.services.task_service import get_all_tasks_from_db, get_chunks_and_tasks_with_scheduled_chunks, get_last_task_with_chunks, get_scheduled_chunks_from_db

# Use get_db() directly
db_generator = get_db()
db: Session = next(db_generator)
# python -m app.core.timeslot
try:
    # arr = get_all_tasks_from_db(db)
    # arr=get_scheduled_chunks_from_db(db)
    # print("All tasks from DB:", arr)

    # total_chunks = sum(len(task["chunks"]) for task in arr)
    # print(total_chunks)
    # arr,chunks=get_chunks_and_tasks_with_scheduled_chunks(db)
    # print("Scheduled chunks from DB:", arr)
    task,chunk=get_last_task_with_chunks(db)
    # print("Last task with chunks from DB:", task, chunk)
    get_scheduled_chunks(db,task,chunk)
finally:
    db_generator.close()  # Close the DB session generator properly



# from datetime import datetime
# import dateutil.parser
# from sqlalchemy import false



# events=[
#     {
#         "Id": "f2q1r6irturlgt5sgmtn8ht6rc",
#         "Subject": "second chunk summary",
#         "StartTime": "2024-12-11T18:30:00+05:30",
#         "EndTime": "2024-12-11T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "lc2gr55uao5ch1369qusmvg2m4",
#         "Subject": "second chunk summary",
#         "StartTime": "2024-12-11T18:30:00+05:30",
#         "EndTime": "2024-12-11T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "mcrugghksedt86s09ts90gjtq8",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-21T18:30:00+05:30",
#         "EndTime": "2025-02-21T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "5mgvbm05tm24df88j3mbnnmm24",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "pb8u2eem6c49th5f5pqejt2ctg",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "v4fessgio2dna2kd3sdomoi970",
#         "Subject": "Untitled Event",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "vtdmhg3ihfm8dqjgkstg50q26c",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "sr35a0gp642bs2j1knks324s6k",
#         "Subject": "Task - TaskType.WORK",
#         "StartTime": "2025-05-27T00:00:00+05:30",
#         "EndTime": "2025-05-27T01:00:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Task: TaskType.WORK, Priority: Priority.HIGH, Chunks: 7"
#     },
#     {
#         "Id": "s27gb5am10r908b8cju9m03j34",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-06-02T18:30:00+05:30",
#         "EndTime": "2025-06-03T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": false,
#         "Location": "",
#         "Description": "Second task description"
#     }
# ]

# def extract_unavailable_timeslots(events):
#     """
#     Extract unavailable time slots from a list of event data.
    
#     Args:
#         events: List of dictionaries containing event data with 'StartTime' and 'EndTime' in ISO 8601 format
    
#     Returns:
#         List of dictionaries with 'start' and 'end' datetime keys for unavailable time slots
#     """
#     unavailable_slots = []
    
#     for event in events:
#         try:
#             # Parse ISO 8601 formatted strings to datetime objects
#             start_time = dateutil.parser.isoparse(event['StartTime'])
#             end_time = dateutil.parser.isoparse(event['EndTime'])
            
#             # Ensure the parsed times are valid
#             if start_time < end_time:
#                 unavailable_slots.append({
#                     'start': start_time,
#                     'end': end_time
#                 })
#         except (KeyError, ValueError):
#             # Skip invalid or missing time data
#             continue
    
#     return unavailable_slots

# unavailable_timeslots = extract_unavailable_timeslots(events)
# print(get_available_timeslots(unavailable_timeslots,
#     datetime(2024, 12, 11),
#     datetime(2025, 6, 3)
# ))

# # Your event data (provided earlier)
# events = [
#     {
#         "Id": "f2q1r6irturlgt5sgmtn8ht6rc",
#         "Subject": "second chunk summary",
#         "StartTime": "2024-12-11T18:30:00+05:30",
#         "EndTime": "2024-12-11T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "lc2gr55uao5ch1369qusmvg2m4",
#         "Subject": "second chunk summary",
#         "StartTime": "2024-12-11T18:30:00+05:30",
#         "EndTime": "2024-12-11T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "mcrugghksedt86s09ts90gjtq8",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-21T18:30:00+05:30",
#         "EndTime": "2025-02-21T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "5mgvbm05tm24df88j3mbnnmm24",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "pb8u2eem6c49th5f5pqejt2ctg",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "v4fessgio2dna2kd3sdomoi970",
#         "Subject": "Untitled Event",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "vtdmhg3ihfm8dqjgkstg50q26c",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-02-25T18:30:00+05:30",
#         "EndTime": "2025-02-25T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     },
#     {
#         "Id": "sr35a0gp642bs2j1knks324s6k",
#         "Subject": "Task - TaskType.WORK",
#         "StartTime": "2025-05-27T00:00:00+05:30",
#         "EndTime": "2025-05-27T01:00:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Task: TaskType.WORK, Priority: Priority.HIGH, Chunks: 7"
#     },
#     {
#         "Id": "s27gb5am10r908b8cju9m03j34",
#         "Subject": "second chunk summary",
#         "StartTime": "2025-06-02T18:30:00+05:30",
#         "EndTime": "2025-06-03T20:30:00+05:30",
#         "Priority": "Medium",
#         "Status": "Scheduled",
#         "IsAllDay": False,
#         "Location": "",
#         "Description": "Second task description"
#     }
# ]

# # Add test unavailable slots to create gaps similar to your example
# events.append({
#     "Id": "test1",
#     "Subject": "Test Event",
#     "StartTime": "2025-02-18T10:00:00+05:30",
#     "EndTime": "2025-02-18T11:00:00+05:30",
#     "Priority": "Medium",
#     "Status": "Scheduled",
#     "IsAllDay": False,
#     "Location": "",
#     "Description": "Test"
# })
# events.append({
#     "Id": "test2",
#     "Subject": "Test Event",
#     "StartTime": "2025-02-18T12:00:00+05:30",
#     "EndTime": "2025-02-18T14:00:00+05:30",
#     "Priority": "Medium",
#     "Status": "Scheduled",
#     "IsAllDay": False,
#     "Location": "",
#     "Description": "Test"
# })

# def get_available_timeslots(unavailable_slots, start_time, end_time, slot_duration=timedelta(minutes=30)):
#     """
#     Find available time slots within a given period, excluding unavailable slots, across multiple days.
#     Only considers time slots between 8:00 AM and 5:00 PM each day, split into 30-minute intervals.
#     Returns naive datetime objects (without timezone).
    
#     Args:
#         unavailable_slots: List of dicts with 'start' and 'end' datetime keys for unavailable times
#         start_time: Datetime for the start of the period
#         end_time: Datetime for the end of the period
#         slot_duration: Timedelta for the duration of each slot (default 30 minutes)
    
#     Returns:
#         List of dicts with 'start' and 'end' naive datetime keys for available slots
#     """
#     # Get timezone from unavailable slots or use local timezone as fallback
#     tzinfo = unavailable_slots[0]['start'].tzinfo if unavailable_slots else tz.tzlocal()
    
#     # Ensure start_time and end_time have the same timezone
#     start_time = start_time.replace(tzinfo=tzinfo) if start_time.tzinfo is None else start_time
#     end_time = end_time.replace(tzinfo=tzinfo) if end_time.tzinfo is None else end_time
    
#     # Sort and clean unavailable slots
#     sorted_slots = []
#     for slot in unavailable_slots:
#         if 'start' in slot and 'end' in slot and slot['start'] < slot['end']:
#             sorted_slots.append(slot)
#     sorted_slots.sort(key=lambda x: x['start'])
    
#     available_slots = []
#     current_day = start_time.date()
#     end_day = end_time.date()
    
#     # Iterate through each day in the period
#     while current_day <= end_day:
#         # Define the day's time window: 8:00 AM to 5:00 PM
#         day_start = datetime.combine(current_day, datetime.strptime("18:00", "%H:%M").time(), tzinfo=tzinfo)
#         day_end = datetime.combine(current_day, datetime.strptime("20:00", "%H:%M").time(), tzinfo=tzinfo)
        
#         # Adjust day_start and day_end if they fall outside the overall period
#         if current_day == start_time.date():
#             day_start = max(day_start, start_time)
#         if current_day == end_day:
#             day_end = min(day_end, end_time)
        
#         # Skip if the adjusted day_end is before or equal to day_start
#         if day_end <= day_start:
#             current_day += timedelta(days=1)
#             continue
        
#         # Generate potential 30-minute slots from 8:00 AM to 5:00 PM
#         current_time = day_start
#         day_slots = []
#         while current_time < day_end:
#             slot_end = min(current_time + slot_duration, day_end)
#             if slot_end <= current_time:
#                 break
#             day_slots.append({'start': current_time, 'end': slot_end})
#             current_time = slot_end
        
#         # Filter out slots that overlap with unavailable slots
#         for slot in day_slots:
#             is_available = True
#             for unavailable in sorted_slots:
#                 # Check if the slot overlaps with an unavailable slot
#                 if not (slot['end'] <= unavailable['start'] or slot['start'] >= unavailable['end']):
#                     is_available = False
#                     break
#             if is_available:
#                 # Convert to naive datetime by removing timezone
#                 naive_start = slot['start'].replace(tzinfo=None)
#                 naive_end = slot['end'].replace(tzinfo=None)
#                 available_slots.append({
#                     'start': naive_start,
#                     'end': naive_end
#                 })
        
#         # Move to the next day
#         current_day += timedelta(days=1)
    
#     return available_slots

# # Custom function to format output like datetime(...)
# def format_datetime(dt):
#     return f"datetime({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute})"

# # Helper function to print slots in the desired format
# def print_available_slots(slots):
#     print("[")
#     for slot in slots:
#         print(f"    {{'start': {format_datetime(slot['start'])}, 'end': {format_datetime(slot['end'])}}},")
#     print("]")

# def extract_unavailable_timeslots(events):
#     """
#     Extract unavailable time slots from a list of event data.
    
#     Args:
#         events: List of dictionaries containing event data with 'StartTime' and 'EndTime' in ISO 8601 format
    
#     Returns:
#         List of dictionaries with 'start' and 'end' datetime keys for unavailable time slots
#     """
#     unavailable_slots = []
    
#     for event in events:
#         try:
#             start_time = dateutil.parser.isoparse(event['StartTime'])
#             end_time = dateutil.parser.isoparse(event['EndTime'])
            
#             if start_time < end_time:
#                 unavailable_slots.append({
#                     'start': start_time,
#                     'end': end_time
#                 })
#         except (KeyError, ValueError):
#             continue
    
#     return unavailable_slots


