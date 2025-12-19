from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    TrainerProfile,
    ClientProfile,
    Specialization,
    Workout,
    Schedule,
    Booking,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff",)
    list_filter = ("role", "is_staff",)
    search_fields = ("username", "email",)
    fieldsets = BaseUserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Role", {"fields": ("role",)}),)


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization",)
    list_filter = ("specialization",)
    fieldsets = [
        ('Main info', {
            'fields': (
                'user', "specialization"
            ),
        }),
        ("Additional info", {
            "fields": ("bio",)
        })
    ]


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone_number",)
    list_filter = ("full_name", "phone_number",)
    fieldsets = (
        (None, {"fields": ("user", "full_name", "phone_number")}),
    )

admin.site.register(Specialization)

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

