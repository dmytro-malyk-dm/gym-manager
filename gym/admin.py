from django.contrib import admin
from django.contrib import admin
from .models import (
    User,
    TrainerProfile,
    ClientProfile,
    Specialization,
    Workout,
    Schedule,
    Booking,
)

admin.site.register(User)
admin.site.register(TrainerProfile)
admin.site.register(ClientProfile)
admin.site.register(Specialization)
admin.site.register(Workout)
admin.site.register(Schedule)
admin.site.register(Booking)

