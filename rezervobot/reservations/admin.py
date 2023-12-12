from django.contrib import admin

from .models import Reservation, StudyRoom


class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity"]


class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        "student_id",
        "study_room",
        "start_at",
        "duration",
    ]


admin.site.register(StudyRoom, StudyRoomAdmin)
admin.site.register(Reservation, ReservationAdmin)
