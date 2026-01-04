from django.conf import settings
from django.db import models
from accounts.models import TrainerProfile, User


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
        Workout, on_delete=models.CASCADE, related_name="schedules"
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
        limit_choices_to={"role": User.Role.CLIENT},
    )
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="bookings"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "schedule")

    def __str__(self):
        return f"{self.client} | {self.schedule}"
