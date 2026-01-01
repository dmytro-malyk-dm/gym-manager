from django.contrib import admin

from .models import (
    Workout,
    Schedule,
    Booking,
)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("name", "trainer")
    search_fields = ("name",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("workout", "start_time", "capacity")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("client", "schedule", "created_at")
