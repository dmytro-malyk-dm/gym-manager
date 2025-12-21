from django.urls import path

from gym.views import (
    HomeTemplateView,
    TrainerListView,
    TrainerDetailView,
    WorkoutDetailView,
    WorkoutListView,
    ScheduleListView, ScheduleDetailView, ClientRegistrationView, BookingCreateView, BookingCancelView
)

app_name = "gym"

urlpatterns = [
    path("", HomeTemplateView.as_view(), name="index"),
    path("trainers/", TrainerListView.as_view(), name="trainer-list"),
    path("trainers/<int:pk>/", TrainerDetailView.as_view(), name="trainer-detail"),
    path("workouts/<int:pk>/", WorkoutDetailView.as_view(), name="workout-detail"),
    path("workouts/", WorkoutListView.as_view(), name="workout-list"),
    path("schedules/", ScheduleListView.as_view(), name="schedule-list"),
    path("schedules/<int:pk>/", ScheduleDetailView.as_view(), name="schedule-detail"),
    path("register/", ClientRegistrationView.as_view(), name="register"),
    path("schedule/<int:pk>/book/", BookingCreateView.as_view(), name="schedule-book"),
    path("schedule/<int:pk>/cancel/", BookingCancelView.as_view(), name="schedule-cancel"),

]
