# Generated by Django 5.0 on 2023-12-11 21:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StudyRoom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250)),
                ("capacity", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_at", models.DateTimeField()),
                ("duration", models.DurationField()),
                ("student_id", models.CharField(max_length=8)),
                (
                    "study_room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reservations.studyroom",
                    ),
                ),
            ],
        ),
    ]
