from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.v1.models.events import Event
from api.v1.schemas.events import EventCreate, EventCreateResponse
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service

events = APIRouter(prefix="/events", tags=["Events"])

@events.post("/", response_model=EventCreateResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    if not current_user.is_superuser:
        event_status = "pending"

    db_event = Event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        created_by=current_user.id,
        status=event_status if not current_user.is_superuser else "approved"
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return EventCreateResponse(
        id=db_event.id,
        title=db_event.title,
        description=db_event.description,
        start_time=db_event.start_time,
        end_time=db_event.end_time,
        location=db_event.location,
        message="Event created successfully"
    )