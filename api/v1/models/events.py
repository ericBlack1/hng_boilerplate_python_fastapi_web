from sqlalchemy import Column, String, DateTime
from api.v1.models.base_model import BaseTableModel

class Event(BaseTableModel):
    __tablename__ = "events"

    title = Column(String, index=True)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String)
