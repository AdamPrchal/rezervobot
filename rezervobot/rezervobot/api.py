from datetime import datetime, timedelta

from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import HttpError
from reservations.models import Reservation, StudyRoom
from reservations.schemas import (
    AvailableRoomsRequest,
    ReservationCreateRequest,
    StudyRoomResponse,
)
from reservations.utils import (
    calculate_availability,
    find_available_room,
    is_room_available,
)

api = NinjaAPI(title="Rezervobot API")

from datetime import datetime


@api.post("/reservations/")
def create_reservation(
    request, reservation_data: ReservationCreateRequest
):
    start_at = timezone.now() + timedelta(
        minutes=reservation_data.start_in
    )
    duration_timedelta = timedelta(minutes=reservation_data.duration)

    available_room = find_available_room(
        reservation_data.required_capacity,
        start_at,
        duration_timedelta,
    )

    if available_room:
        reservation = Reservation(
            start_at=start_at,
            duration=duration_timedelta,
            student_id=reservation_data.student_id,
            study_room=available_room,
        )
        reservation.save()

        start_time_formatted = start_at.strftime("%H:%M")
        end_time_formatted = (start_at + duration_timedelta).strftime(
            "%H:%M"
        )

        message = (
            f"Tak {available_room.name} je v {start_time_formatted} tvoje na {reservation_data.duration} minut. "
            f"Prosím, v {end_time_formatted} prosím uvolni studovnu. Ať se daří!"
        )
        return {"result": "success", "message": message}
    else:
        return {
            "result": "failure",
            "message": "Omlouváme se, ale v tuto chvíli není k dispozici žádná studovna, která by vyhovovala vašim požadavkům na kapacitu a čas. Zkuste to prosím později nebo upravte vaše požadavky.",
        }


@api.post("/study-rooms/available/")
def list_available_study_rooms(
    request, room_request: AvailableRoomsRequest
):
    start_at = timezone.now() + timedelta(
        minutes=room_request.start_in
    )
    duration_timedelta = timedelta(minutes=room_request.duration)
    available_rooms = []

    for room in StudyRoom.objects.filter(
        capacity__gte=room_request.required_capacity
    ):
        if is_room_available(room.id, start_at, duration_timedelta):
            (
                next_available_time,
                available_duration,
            ) = calculate_availability(room, start_at)

            if (
                next_available_time <= start_at
                and available_duration >= duration_timedelta
            ):
                available_rooms.append(
                    {
                        "id": room.id,
                        "name": room.name,
                        "capacity": room.capacity,
                        "next_available_time": next_available_time,
                        "available_duration": available_duration,
                    }
                )

    if available_rooms:
        return {
            "result": "success",
            "available_rooms": available_rooms,
        }
    else:
        return {
            "result": "failure",
            "message": "Nebyly nalezeny žádné dostupné studovny odpovídající vašim požadavkům.",
        }
