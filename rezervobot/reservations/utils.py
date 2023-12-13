from datetime import timedelta

from django.utils import timezone

from .models import Reservation, StudyRoom


def find_available_room(required_capacity, start_at, duration):
    # Získáme všechny studovny s dostatečnou kapacitou
    suitable_rooms = StudyRoom.objects.filter(
        capacity__gte=required_capacity
    )

    for room in suitable_rooms:
        # Kontrolujeme dostupnost každé studovny
        if is_room_available(room.id, start_at, duration):
            return room
    return None


def is_room_available(study_room_id, start_at, duration):
    end_at = start_at + duration
    overlapping_reservations = Reservation.objects.filter(
        study_room_id=study_room_id, start_at__lt=end_at
    )

    for reservation in overlapping_reservations:
        reservation_end_at = (
            reservation.start_at + reservation.duration
        )
        if reservation_end_at > start_at:
            # Existuje překrývající se rezervace
            return False

    return True


def find_next_available_time(
    study_room_id, required_duration, start_in
):
    # Získáme aktuální čas a připočítáme k němu 'start_in'
    start_time = timezone.now() + timedelta(minutes=start_in)

    # Hledáme rezervace, které končí po 'start_time'
    relevant_reservations = Reservation.objects.filter(
        study_room_id=study_room_id,
        start_at__lt=start_time
        + timedelta(minutes=required_duration),
    ).order_by("start_at")

    current_time = start_time
    for reservation in relevant_reservations:
        reservation_end_at = (
            reservation.start_at + reservation.duration
        )
        if reservation_end_at <= current_time:
            continue

        if reservation.start_at - current_time >= timedelta(
            minutes=required_duration
        ):
            break

        current_time = max(current_time, reservation_end_at)

    return int((current_time - start_time + timedelta(minutes=start_in)).total_seconds() / 60)
