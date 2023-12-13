from datetime import datetime, timedelta

from ninja import Schema
from pydantic import constr


class ReservationCreateRequest(Schema):
    start_in: int  # Čas začátku rezervace v minutách od nynějška
    duration: int  # Délka rezervace v minutách
    student_id: constr(max_length=8)
    required_capacity: int
