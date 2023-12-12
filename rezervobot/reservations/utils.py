from datetime import timedelta

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


def calculate_availability(study_room, current_time):
    future_reservations = Reservation.objects.filter(
        study_room=study_room,
        start_at__gte=current_time
    ).order_by('start_at')

    if not future_reservations.exists():
        # Pokud neexistují žádné budoucí rezervace, studovna je dostupná ihned až do konce dne
        end_of_day = current_time.replace(hour=23, minute=59, second=59)
        return current_time, end_of_day - current_time

    next_available_time = current_time
    for reservation in future_reservations:
        end_at = reservation.start_at + reservation.duration
        if reservation.start_at >= next_available_time:
            # Našli jsme slot, kdy je studovna volná
            available_duration = reservation.start_at - next_available_time
            return next_available_time, available_duration
        next_available_time = max(next_available_time, end_at)

    # Pokud nebyl nalezen volný slot, vrátíme čas do konce dne
    end_of_day = next_available_time.replace(hour=23, minute=59, second=59)
    return next_available_time, end_of_day - next_available_time



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
