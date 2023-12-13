from datetime import timedelta

from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import HttpError
from reservations.models import Reservation, StudyRoom
from reservations.schemas import ReservationCreateRequest
from reservations.utils import (
    find_available_room,
    find_next_available_time,
)

api = NinjaAPI(title="Rezervobot API")


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

        start_time_formatted = timezone.localtime(start_at).strftime(
            "%H:%M"
        )
        end_time_formatted = timezone.localtime(
            start_at + duration_timedelta
        ).strftime("%H:%M")

        message = (
            f"Tak {available_room.name} je v {start_time_formatted} tvoje/vaše na {reservation_data.duration} minut. "
            f"\nProsím, v {end_time_formatted} uvolni/uvolněte studovnu pro další. Ať se daří!"
        )
        return {"result": "success", "message": message}
    else:
        return {
            "result": "failure",
            "message": "Omlouvám se, ale není k dispozici žádná studovna, která by vyhovovala požadavkům na kapacitu a čas.\nZkuste to prosím později nebo uprav požadavky.",
        }


@api.post("/next-available-time/")
def get_next_available_time(
    request, reservation_data: ReservationCreateRequest
):
    # Vypočítáme 'start_at' od aktuálního času plus 'start_in'
    start_in_from_now = timezone.now() + timedelta(
        minutes=reservation_data.start_in
    )
    duration_timedelta = timedelta(minutes=reservation_data.duration)

    # Prohledáme každou studovnu pro nalezení nejbližšího volného času
    earliest_available_time_in_minutes = None
    for room in StudyRoom.objects.filter(
        capacity__gte=reservation_data.required_capacity
    ):
        available_time_in_minutes = find_next_available_time(
            room.id,
            reservation_data.duration,
            reservation_data.start_in,
        )
        if (
            earliest_available_time_in_minutes is None
            or available_time_in_minutes
            < earliest_available_time_in_minutes
        ):
            earliest_available_time_in_minutes = (
                available_time_in_minutes
            )

    if earliest_available_time_in_minutes is not None:
        return {
            "start_in": earliest_available_time_in_minutes,
            "result": "success",
        }
    else:
        return {
            "start_in": None,
            "message": "Nejsou dostupná žádná okna v požadovaném časovém rozsahu.",
            "result": "failure",
        }
