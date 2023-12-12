from datetime import datetime, timedelta

from ninja import Schema
from pydantic import constr


class ReservationCreateRequest(Schema):
    start_at: datetime
    duration: int
    student_id: constr(max_length=8)
    required_capacity: int


class AvailableRoomsRequest(Schema):
    start_at: datetime
    duration: int  # Délka rezervace v minutách
    required_capacity: int

class StudyRoomResponse(Schema):
    id: int
    name: str
    capacity: int
    next_available_time: datetime
    available_duration: timedelta

