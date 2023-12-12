from django.db import models


class StudyRoom(models.Model):
    name = models.CharField(max_length=250)
    capacity = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Reservation(models.Model):
    start_at = models.DateTimeField()
    duration = models.DurationField()
    student_id = models.CharField(max_length=8)
    study_room = models.ForeignKey(
        StudyRoom, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.student_id} - {self.study_room}"
