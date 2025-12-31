from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User, TrainerProfile, ClientProfile, Specialization


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role"]
    list_filter = ["role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "specialization"]
    list_filter = ["specialization"]


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ["name"]
