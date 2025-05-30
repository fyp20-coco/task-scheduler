import math
import random
import copy
from datetime import datetime, timedelta
from dateutil import tz
import dateutil
from sqlalchemy import false
from app.core.database import get_db

from app.api import events
from app.core.utills import get_chunks_and_tasks_with_scheduled_chunks, get_last_task_with_chunks
from app.services.calendar_service import get_event_timeframe





###############################
# Data Structures & Simulated Data
###############################

class Task:
    def __init__(self, id, priority, deadline, created_at, user_id, typ):
        self.id = id
        self.priority = priority  # 'HIGH','MEDIUM','LOW'
        self.deadline = deadline  # datetime object
        self.created_at = created_at
        self.user_id = user_id
        self.typ = typ  


class Chunk:
    def __init__(self, id, task_id, chunk_index, description, title, time):
        self.id = id
        self.task_id = task_id
        self.chunk_index = chunk_index  # order within the task
        self.description = description
        self.title = title
        self.chunk = time


# Create three sample tasks.
tasks = [
    Task(id=1, priority='LOW', deadline=datetime(2025, 2, 18, 12, 0),
         created_at=datetime(2025, 2, 17, 9, 0), user_id=101, typ='WORK'),
    Task(id=2, priority='MEDIUM', deadline=datetime(2025, 2, 18, 15, 0),
         created_at=datetime(2025, 2, 17, 10, 0), user_id=102, typ='HOME'),
    Task(id=3, priority='HIGH', deadline=datetime(2025, 2, 18, 10, 30),
         created_at=datetime(2025, 2, 18, 7, 0), user_id=103, typ='WORK')
]

# Create chunks for each task (each chunk assumed to require 30 minutes scheduling)
chunks = [
    Chunk(id=101, task_id=1, chunk_index=1, description="Task1-Part1", title="T1.1", time="10:00"),
    Chunk(id=102, task_id=1, chunk_index=2, description="Task1-Part2", title="T1.2", time="10:00"),
    Chunk(id=201, task_id=2, chunk_index=1, description="Task2-Part1", title="T2.1", time="10:00"),
    Chunk(id=202, task_id=2, chunk_index=2, description="Task2-Part2", title="T2.2", time="10:00"),
    Chunk(id=203, task_id=2, chunk_index=3, description="Task2-Part3", title="T2.3", time="10:00"),
    Chunk(id=301, task_id=3, chunk_index=1, description="Urgent-Task3-Part1", title="T3.1", time="10:00"),
    Chunk(id=302, task_id=3, chunk_index=2, description="Urgent-Task3-Part2", title="T3.2", time="10:00")
]

# A lookup dictionary for tasks (used for deadline and other checks)
tasks_dict = {t.id: t for t in tasks}

# Available time slots stored as list of dicts; each slot must be divided into 30-min blocks.
timeslots = [
    {"start": datetime(2025, 2, 18, 9, 0), "end": datetime(2025, 2, 18, 10, 0)},
    {"start": datetime(2025, 2, 18, 11, 0), "end": datetime(2025, 2, 18, 12, 0)},
    {"start": datetime(2025, 2, 18, 14, 0), "end": datetime(2025, 2, 18, 15, 30)},
]

# For each timeslot, compute the number of 30-min blocks available.
for slot in timeslots:
    duration = (slot["end"] - slot["start"]).seconds // 60  # duration in minutes
    slot["capacity"] = duration // 30

CHUNK_DURATION = timedelta(minutes=30)


###############################
# MCTS State & Methods
###############################

class ScheduleState:
    def __init__(self, unscheduled_chunks, assignments, chunks, tasks_dict):
        # unscheduled_chunks: list of Chunk objects
        # assignments: dict mapping slot index to list of assignments (tuple: (chunk, start_time, end_time))
        self.unscheduled_chunks = unscheduled_chunks
        self.assignments = assignments  # e.g., {0: [(chunk, start_time, end_time), ...]}
        self.chunks = chunks  # List of all chunks
        self.tasks_dict = tasks_dict  # Dictionary mapping task_id to Task object
        
    def copy(self):
        return ScheduleState(self.unscheduled_chunks.copy(),
                             {k: v.copy() for k, v in self.assignments.items()},
                             self.chunks,
                             self.tasks_dict)

    def is_terminal(self):
        return len(self.unscheduled_chunks) == 0

    def possible_actions(self):
        actions = []
        for chunk in self.unscheduled_chunks:
            for slot_index, slot in enumerate(timeslots):
                current_assignments = self.assignments.get(slot_index, [])
                if len(current_assignments) < slot["capacity"]:
                    actions.append((chunk, slot_index))
        return actions

    def apply_action(self, action):
        # Action: (chunk, slot_index)
        new_state = self.copy()
        chunk, slot_index = action
        new_state.unscheduled_chunks.remove(chunk)
        current_assignments = new_state.assignments.get(slot_index, [])
        assigned_count = len(current_assignments)
        start_time = timeslots[slot_index]["start"] + CHUNK_DURATION * assigned_count
        end_time = start_time + CHUNK_DURATION
        new_assignment = (chunk, start_time, end_time)
        new_state.assignments.setdefault(slot_index, []).append(new_assignment)
        return new_state


###############################
# Self-Critic Function
###############################

def self_critic(state, tasks_dict):
    """
    Evaluate a complete schedule:
      - Deadline misses: -2 for each assignment starting after its task deadline.
      - Dependency violations: -3 if chunks of the same task are scheduled out of order.
      - Balanced load: +2 if the number of assignments per timeslot does not vary much.
      - Task clustering: +1 if chunks from the same task are in adjacent or the same timeslot.
      - Completion bonus: +10 if the schedule is terminal.
    """
    score = 0
    # 1. Deadline misses.
    for slot_index, assignments in state.assignments.items():
        for (chunk, start_time, _) in assignments:
            task = tasks_dict.get(chunk.task_id)
            if task and start_time > task.deadline:
                score -= 2

    # 2. Dependency violations.
    task_assignments = {}
    for slot_index, assignments in state.assignments.items():
        for (chunk, start_time, _) in assignments:
            task_assignments.setdefault(chunk.task_id, []).append((chunk.chunk_index, slot_index, start_time))
    for task_id, entries in task_assignments.items():
        entries_sorted = sorted(entries, key=lambda x: x[0])  # sort by chunk_index
        slot_nums = [entry[1] for entry in entries_sorted]
        if slot_nums != sorted(slot_nums):
            score -= 3

    # 3. Balanced load.
    slot_counts = [len(state.assignments.get(i, [])) for i in range(len(timeslots))]
    avg = sum(slot_counts) / len(timeslots)
    variance = sum((count - avg) ** 2 for count in slot_counts) / len(timeslots)
    if math.sqrt(variance) <= 1:
        score += 2

    # 4. Task clustering.
    for task_id, entries in task_assignments.items():
        slot_indices = [entry[1] for entry in entries]
        if max(slot_indices) - min(slot_indices) <= 1:
            score += 1

    # 5. Completion bonus.
    if state.is_terminal():
        score += 10

    return score


###############################
# Rollout Policy (Random Completion)
###############################

def rollout(state, tasks_dict):
    current_state = state.copy()
    while not current_state.is_terminal():
        actions = current_state.possible_actions()
        if not actions:
            break
        action = random.choice(actions)
        current_state = current_state.apply_action(action)
    return self_critic(current_state,tasks_dict)


###############################
# MCTS Node & Search
###############################

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions = state.possible_actions()

    def ucb_value(self, child, c=1.41):
        if child.visits == 0:
            return float('inf')
        return (child.total_reward / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c=1.41):
        return max(self.children.values(), key=lambda n: self.ucb_value(n, c))


def tree_policy(node):
    current = node
    while not current.state.is_terminal():
        if not current.is_fully_expanded():
            return expand(current)
        else:
            current = current.best_child()
    return current


def expand(node):
    action = node.untried_actions.pop(random.randrange(len(node.untried_actions)))
    new_state = node.state.apply_action(action)
    child_node = MCTSNode(new_state, parent=node)
    node.children[action] = child_node
    return child_node


def backpropagate(node, reward):
    current = node
    while current is not None:
        current.visits += 1
        current.total_reward += reward
        current = current.parent


def mcts(root_state, tasks_dict, iterations=1000):
    root_node = MCTSNode(root_state)
    best_complete_state = None
    best_reward = -float('inf')

    for i in range(iterations):
        node = tree_policy(root_node)
        reward = rollout(node.state, tasks_dict)
        backpropagate(node, reward)
        if node.state.is_terminal() and reward > best_reward:
            best_reward = reward
            best_complete_state = node.state
    return best_complete_state, best_reward


###############################
# Main Simulation & MySQL Storage
###############################

def schedule_task(tasks_dict, unscheduled_chunks, timeslots):
    """ Schedules a task based on the provided chunks. """
    initial_state = ScheduleState(unscheduled_chunks=unscheduled_chunks.copy(), assignments={}, chunks=unscheduled_chunks, tasks_dict=tasks_dict)
    final_state, final_score = mcts(initial_state, tasks_dict, iterations=2000)
    print("Final schedule score:", final_score)
    for slot_index in range(len(timeslots)):
        assignments = final_state.assignments.get(slot_index, [])
        print(
            f"\nTime slot {slot_index} ({timeslots[slot_index]['start'].strftime('%H:%M')} - {timeslots[slot_index]['end'].strftime('%H:%M')}):")
        for (chunk, start, end) in assignments:
            task = tasks_dict.get(chunk.task_id)
            print(
                f"  Task {task.id} (Priority: {task.priority}), Chunk {chunk.chunk_index} scheduled from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")

    print("\nScheduled chunks:", final_state.assignments)

def get_available_timeslots(unavailable_slots, start_time, end_time, slot_duration=timedelta(minutes=30)):
    """
    Find available time slots within a given period, excluding unavailable slots, across multiple days.
    Only considers time slots between 6:00 PM and 8:00 PM each day, split into 30-minute intervals.
    Returns naive datetime objects (without timezone).
    
    Args:
        unavailable_slots: List of dicts with 'start' and 'end' datetime keys for unavailable times
        start_time: Datetime for the start of the period
        end_time: Datetime for the end of the period
        slot_duration: Timedelta for the duration of each slot (default 30 minutes)
    
    Returns:
        List of dicts with 'start' and 'end' naive datetime keys for available slots
    """
    # Use local timezone as fallback
    tzinfo = tz.tzlocal()
    
    # Ensure start_time and end_time are datetime objects with timezone
    if isinstance(start_time, str):
        start_time = dateutil.parser.isoparse(start_time)
    if isinstance(end_time, str):
        end_time = dateutil.parser.isoparse(end_time)
    
    start_time = start_time.replace(tzinfo=tzinfo) if start_time.tzinfo is None else start_time
    end_time = end_time.replace(tzinfo=tzinfo) if end_time.tzinfo is None else end_time
    
    # Sort and clean unavailable slots
    sorted_slots = []
    for slot in unavailable_slots or []:
        try:
            if 'start' in slot and 'end' in slot and isinstance(slot['start'], datetime) and isinstance(slot['end'], datetime):
                if slot['start'] < slot['end']:
                    sorted_slots.append(slot)
        except (KeyError, TypeError):
            continue
    sorted_slots.sort(key=lambda x: x['start'])
    
    available_slots = []
    current_day = start_time.date()
    end_day = end_time.date()
    
    # Iterate through each day in the period
    while current_day <= end_day:
        # Define the day's time window: 6:00 PM to 8:00 PM
        day_start = datetime.combine(current_day, datetime.strptime("18:00", "%H:%M").time(), tzinfo=tzinfo)
        day_end = datetime.combine(current_day, datetime.strptime("20:00", "%H:%M").time(), tzinfo=tzinfo)
        
        # Adjust day_start and day_end if they fall outside the overall period
        if current_day == start_time.date():
            day_start = max(day_start, start_time)
        if current_day == end_day:
            day_end = min(day_end, end_time)
        
        # Skip if the adjusted day_end is before or equal to day_start
        if day_end <= day_start:
            current_day += timedelta(days=1)
            continue
        
        # Generate potential 30-minute slots from 6:00 PM to 8:00 PM
        current_time = day_start
        day_slots = []
        while current_time < day_end:
            slot_end = min(current_time + slot_duration, day_end)
            if slot_end <= current_time:
                break
            day_slots.append({'start': current_time, 'end': slot_end})
            current_time = slot_end
        
        # Filter out slots that overlap with unavailable slots
        for slot in day_slots:
            is_available = True
            for unavailable in sorted_slots:
                if not (slot['end'] <= unavailable['start'] or slot['start'] >= unavailable['end']):
                    is_available = False
                    break
            if is_available:                # Convert to naive datetime by removing timezone
                naive_start = slot['start'].replace(tzinfo=None)
                naive_end = slot['end'].replace(tzinfo=None)
                # Calculate capacity: number of 30-min blocks that can fit
                duration = (naive_end - naive_start).seconds // 60  # duration in minutes
                capacity = duration // 30
                available_slots.append({
                    'start': naive_start,
                    'end': naive_end,
                    'capacity': capacity
                })
        
        # Move to the next day
        current_day += timedelta(days=1)
    
    return available_slots

# Custom function to format output like datetime(...)
def format_datetime(dt):
    return f"datetime({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute})"

# Helper function to print slots in the desired format
def print_available_slots(slots):
    print("[")
    for slot in slots:
        print(f"    {{'start': {format_datetime(slot['start'])}, 'end': {format_datetime(slot['end'])}}},")
    print("]")

def extract_unavailable_timeslots(events):
    """
    Extract unavailable time slots from a list of event data.
    
    Args:
        events: List of dictionaries containing event data with 'StartTime' and 'EndTime' in ISO 8601 format
    
    Returns:
        List of dictionaries with 'start' and 'end' datetime keys for unavailable time slots
    """
    unavailable_slots = []
    
    for event in events:
        try:
            start_time = dateutil.parser.isoparse(event['StartTime'])
            end_time = dateutil.parser.isoparse(event['EndTime'])
            
            if start_time < end_time:
                unavailable_slots.append({
                    'start': start_time,
                    'end': end_time
                })
        except (KeyError, ValueError):
            continue
    
    return unavailable_slots

def main():
    # This function is for testing/demonstration purposes
    # In a real scenario, you would get these from the database
    from datetime import datetime
    
    # Example tasks and chunks (commented out in the actual code)
    class DummyTask:
        def __init__(self, id, priority, deadline, created_at, user_id, typ):
            self.id = id
            self.priority = priority  # 'HIGH','MEDIUM','LOW'
            self.deadline = deadline  # datetime object
            self.created_at = created_at
            self.user_id = user_id
            self.typ = typ  

    class DummyChunk:
        def __init__(self, id, task_id, chunk_index, description, title, time):
            self.id = id
            self.task_id = task_id
            self.chunk_index = chunk_index  # order within the task
            self.description = description
            self.title = title
            self.time = time
    
    # Create test data
    dummy_tasks = [
        DummyTask(id=1, priority='LOW', deadline=datetime(2025, 2, 18, 12, 0),
             created_at=datetime(2025, 2, 17, 9, 0), user_id=101, typ='WORK'),
    ]
    
    dummy_chunks = [
        DummyChunk(id=101, task_id=1, chunk_index=1, description="Test Chunk", title="Test", time="00:30"),
    ]
    
    dummy_tasks_dict = {t.id: t for t in dummy_tasks}
    
    # Test timeslots
    dummy_timeslots = [
        {"start": datetime(2025, 2, 18, 9, 0), "end": datetime(2025, 2, 18, 10, 0), "capacity": 2},
    ]
    
    global timeslots
    timeslots = dummy_timeslots
    
    # Initial state: all chunks unscheduled
    initial_state = ScheduleState(unscheduled_chunks=dummy_chunks.copy(), assignments={}, chunks=dummy_chunks, tasks_dict=dummy_tasks_dict)
    final_state, final_score = mcts(initial_state, dummy_tasks_dict, iterations=2000)
    print("Final schedule score:", final_score)
    for slot_index in range(len(timeslots)):
        assignments = final_state.assignments.get(slot_index, [])
        print(
            f"\nTime slot {slot_index} ({timeslots[slot_index]['start'].strftime('%H:%M')} - {timeslots[slot_index]['end'].strftime('%H:%M')}):")
        for (chunk, start, end) in assignments:
            task = dummy_tasks_dict.get(chunk.task_id)
            print(
                f"  Task {task.id} (Priority: {task.priority}), Chunk {chunk.chunk_index} scheduled from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")

    print("\nScheduled chunks:", final_state.assignments)
    # ##############################
    # # Store Scheduled Chunks into MySQL
    # ###############################

    # # MySQL's connection configuration (update with your actual connection details)
    # config = {
    #     "host": "localhost",
    #     "user": "root",  # Replace with your MySQL username
    #     "password": "root",  # Replace with your MySQL password
    #     "database": "task_db"  # Replace with your database name
    # }

    # try:
    #     conn = mysql.connector.connect(**config)
    #     cursor = conn.cursor()
    #     # Create the scheduled_chunks table if it does not exist.
    #     create_table_query = """
    #     CREATE TABLE IF NOT EXISTS scheduled_chunks (
    #         event_id BIGINT NOT NULL,
    #         chunk_id INT NOT NULL,
    #         start_time DATETIME NOT NULL,
    #         end_time DATETIME NOT NULL,
    #         PRIMARY KEY (event_id, chunk_id)
    #     )
    #     """
    #     cursor.execute(create_table_query)
    #     conn.commit()

    #     # Insert each assignment into scheduled_chunks.
    #     insert_query = """
    #     INSERT INTO scheduled_chunks (event_id, chunk_id, start_time, end_time)
    #     VALUES (%s, %s, %s, %s)
    #     """
    #     for slot_index, assignments in final_state.assignments.items():
    #         for (chunk, start, end) in assignments:
    #             event_id = chunk.task_id
    #             cursor.execute(insert_query, (
    #                 event_id,
    #                 chunk.id,
    #                 start.strftime("%Y-%m-%d %H:%M:%S"),
    #                 end.strftime("%Y-%m-%d %H:%M:%S")
    #             ))
    #     conn.commit()
    #     print("\nScheduled chunks have been stored in the MySQL database (table: scheduled_chunks).")

    #     # Optionally, retrieve and print the stored rows.
    #     cursor.execute("SELECT event_id, chunk_id, start_time, end_time FROM scheduled_chunks")
    #     print("\nStored rows in scheduled_chunks:")
    #     for row in cursor.fetchall():
    #         print(row)

    # except mysql.connector.Error as err:
    #     print("MySQL error:", err)
    # finally:
    #     if conn.is_connected():
    #         cursor.close()
    #         conn.close()



def get_scheduled_chunks(db, start, end):
    """
    Get scheduled chunks for a specified time period using MCTS algorithm.
    
    Args:
        db: Database session
        start: Start datetime
        end: End datetime
        
    Returns:
        Dictionary mapping slot index to list of assignments
    """
    # Get all tasks and chunks from database
    tasks, chunks = get_chunks_and_tasks_with_scheduled_chunks(db)
    tasks2, chunks2 = get_last_task_with_chunks(db)
    
    # Combine all tasks and chunks
    tasks.extend(tasks2)
    chunks.extend(chunks2)
    
    # Create task dictionary for quick lookups
    tasks_dict = {t.id: t for t in tasks}
    
    print("\nRetrieved tasks and chunks for scheduling:")
    print(f"Number of tasks: {len(tasks)}")
    print(f"Number of chunks: {len(chunks)}")
    
    # Validate chunks
    valid_chunks = []
    for chunk in chunks:
        if chunk.task_id not in tasks_dict:
            print(f"Warning: Chunk {chunk.id} references non-existent task_id {chunk.task_id}. Skipping.")
            continue
        valid_chunks.append(chunk)
    
    if not valid_chunks:
        raise ValueError("No valid chunks to schedule.")
    
    # Parse start and end if strings
    if isinstance(start, str):
        start = dateutil.parser.isoparse(start)
    if isinstance(end, str):
        end = dateutil.parser.isoparse(end)
    
    events = get_event_timeframe(start, end)
    unavailable_timeslots = extract_unavailable_timeslots(events)
    available_slots = get_available_timeslots(unavailable_timeslots, start, end)    # Update global timeslots for MCTS
    global timeslots
    timeslots = available_slots
    
    # Initialize MCTS state
    initial_state = ScheduleState(
        unscheduled_chunks=valid_chunks.copy(),
        assignments={},
        chunks=valid_chunks,
        tasks_dict=tasks_dict
    )
    
    # Run MCTS algorithm
    final_state, final_score = mcts(initial_state, tasks_dict, iterations=2000)
    print("Final schedule score:", final_score)
    for slot_index in range(len(available_slots)):
        assignments = final_state.assignments.get(slot_index, [])
        print(
            f"\nTime slot {slot_index} ({available_slots[slot_index]['start'].strftime('%H:%M')} - {available_slots[slot_index]['end'].strftime('%H:%M')}):")
        for (chunk, start, end) in assignments:
            task = tasks_dict.get(chunk.task_id)
            if task is None:
                print(f"Error: No task found for chunk {chunk.id} with task_id {chunk.task_id}. Skipping.")
                continue
            print(
                f"  Task {task.id} (Priority: {task.priority}), Chunk {chunk.chunk_index} scheduled from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")    # Prepare a more structured output
    scheduled_results = {}
    for slot_index, assignments in final_state.assignments.items():
        slot_start = available_slots[slot_index]['start'].strftime('%Y-%m-%d %H:%M:%S')
        slot_end = available_slots[slot_index]['end'].strftime('%Y-%m-%d %H:%M:%S')
        
        scheduled_results[slot_index] = {
            'slot': {
                'start': slot_start,
                'end': slot_end
            },
            'assignments': []
        }
        
        for chunk, start_time, end_time in assignments:
            task = tasks_dict.get(chunk.task_id)
            if task:
                scheduled_results[slot_index]['assignments'].append({
                    'chunk_id': chunk.id,
                    'chunk_index': chunk.chunk_index,
                    'task_id': chunk.task_id,
                    'task_priority': task.priority,
                    'task_type': task.typ,
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    print(f"\nScheduling complete. Successfully scheduled {sum(len(slot['assignments']) for slot in scheduled_results.values())} chunks")
    return final_state.assignments
    # return tasks
# # Create three sample tasks.
# tasks = [
#     Task(id=1, priority='LOW', deadline=datetime(2025, 2, 18, 12, 0),
#          created_at=datetime(2025, 2, 17, 9, 0), user_id=101, typ='WORK'),
#     Task(id=2, priority='MEDIUM', deadline=datetime(2025, 2, 18, 15, 0),
#          created_at=datetime(2025, 2, 17, 10, 0), user_id=102, typ='HOME'),
#     Task(id=3, priority='HIGH', deadline=datetime(2025, 2, 18, 10, 30),
#          created_at=datetime(2025, 2, 18, 7, 0), user_id=103, typ='WORK')
# ]

# # Create chunks for each task (each chunk assumed to require 30 minutes scheduling)
# chunks = [
#     Chunk(id=101, task_id=1, chunk_index=1, description="Task1-Part1", title="T1.1", time="10:00"),
#     Chunk(id=102, task_id=1, chunk_index=2, description="Task1-Part2", title="T1.2", time="10:00"),
#     Chunk(id=201, task_id=2, chunk_index=1, description="Task2-Part1", title="T2.1", time="10:00"),
#     Chunk(id=202, task_id=2, chunk_index=2, description="Task2-Part2", title="T2.2", time="10:00"),
#     Chunk(id=203, task_id=2, chunk_index=3, description="Task2-Part3", title="T2.3", time="10:00"),
#     Chunk(id=301, task_id=3, chunk_index=1, description="Urgent-Task3-Part1", title="T3.1", time="10:00"),
#     Chunk(id=302, task_id=3, chunk_index=2, description="Urgent-Task3-Part2", title="T3.2", time="10:00")
# ]

# # A lookup dictionary for tasks (used for deadline and other checks)
# tasks_dict = {t.id: t for t in tasks}
    



if __name__ == "__main__":
    main()


    unavailable_timeslots = extract_unavailable_timeslots(events)
    print("Unavailable Timeslots:", unavailable_timeslots)
    available_slots=get_available_timeslots(unavailable_timeslots,
        datetime(2024, 12, 11),
        datetime(2024, 12, 13)
    )
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",available_slots)
    print(len(available_slots))