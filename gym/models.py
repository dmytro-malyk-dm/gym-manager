from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", _("Client")
        TRAINER = "trainer", _("Trainer")
        ADMIN = "admin", _("Admin")
    role = models.CharField(
        max_length=63,
        choices=Role.choices,
        default=Role.CLIENT
    )

    def __str__(self):
        return self.username


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_profile"
    )
    bio = models.TextField(blank=True)
    specialization = models.ForeignKey(
        "Specialization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="trainers"
    )

    def __str__(self):
        return self.user.username


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )
    phone_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone_number})"


class Specialization(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Workout(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()
    duration_time = models.PositiveIntegerField()
    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="workouts",
    )

    def __str__(self):
        return self.name


class Schedule(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    start_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.workout.name} | {self.start_time}"

class Booking(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        limit_choices_to={"role": User.Role.CLIENT}
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "schedule")

    def __str__(self):
        return f"{self.client} | {self.schedule}"
