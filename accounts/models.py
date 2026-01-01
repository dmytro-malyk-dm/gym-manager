from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", _("Client")
        TRAINER = "trainer", _("Trainer")
        ADMIN = "admin", _("Admin")

    role = models.CharField(max_length=63, choices=Role.choices, default=Role.CLIENT)

    def __str__(self):
        return self.username


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )
    bio = models.TextField(blank=True)
    specialization = models.ForeignKey(
        "Specialization", on_delete=models.SET_NULL, null=True, related_name="trainers"
    )

    def __str__(self):
        return self.user.username


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone_number})"


class Specialization(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name
