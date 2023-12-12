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
    duration_timedelta = timedelta(minutes=reservation_data.duration)

    available_room = find_available_room(
        reservation_data.required_capacity,
        reservation_data.start_at,
        duration_timedelta,
    )

    if available_room:
        reservation = Reservation(
            start_at=reservation_data.start_at,
            duration=duration_timedelta,
            student_id=reservation_data.student_id,
            study_room=available_room,
        )
        reservation.save()
        return {
            "message": f"Reservation created successfully in room {available_room.name}"
        }
    else:
        raise HttpError(
            400, "No available room with the required capacity"
        )


@api.post("/study-rooms/available/")
def list_available_study_rooms(
    request, room_request: AvailableRoomsRequest
):
    duration_timedelta = timedelta(minutes=room_request.duration)
    available_rooms = []

    for room in StudyRoom.objects.filter(
        capacity__gte=room_request.required_capacity
    ):
        if is_room_available(
            room.id, room_request.start_at, duration_timedelta
        ):
            (
                next_available_time,
                available_duration,
            ) = calculate_availability(room, room_request.start_at)

            # Přidáme pouze pokud je dostupná v požadovaném čase
            if (
                next_available_time <= room_request.start_at
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

    return available_rooms