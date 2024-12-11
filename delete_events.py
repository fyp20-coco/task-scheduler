from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.db_models import ChunkDB
from sqlalchemy import select
from quickstart import delete_event

def delete_events(db: Session):
    result = db.execute(select(ChunkDB.event_id))
    rows=[row[0] for row in result.fetchall()]
    return rows

db = next(get_db())

# Call the function
events = delete_events(db)
filtered_event_ids = [event_id for event_id in events if event_id]

print(filtered_event_ids)
for i in range(len(filtered_event_ids)):
    delete_event(filtered_event_ids[i])