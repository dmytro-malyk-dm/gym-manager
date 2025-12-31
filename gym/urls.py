from django.urls import path

from gym.views import (
    HomeTemplateView,
    TrainerListView,
    TrainerDetailView,
    WorkoutDetailView,
    WorkoutListView,
    ScheduleListView,
    ScheduleDetailView,
    ClientRegistrationView,
    BookingCreateView,
    BookingCancelView,
    MyBookingView,
    ScheduleUpdateView,
    ScheduleDeleteView,
    ScheduleCreateView,
    TrainerCreateView,
    TrainerUpdateView,
    WorkoutCreateView,
    WorkoutUpdateView, WorkoutDeleteView
)

app_name = "gym"

urlpatterns = [
    path("", HomeTemplateView.as_view(), name="index"),
    path("trainers/", TrainerListView.as_view(), name="trainer-list"),
    path(
        "trainers/<int:pk>/",
        TrainerDetailView.as_view(),
        name="trainer-detail"
    ),
    path("trainers/create/", TrainerCreateView.as_view(), name="trainer-create"),
    path("trainers/<int:pk>/update/", TrainerUpdateView.as_view(), name="trainer-update"),
    path(
        "workouts/",
        WorkoutListView.as_view(),
        name="workout-list"
    ),
    path(
        "workouts/<int:pk>/",
        WorkoutDetailView.as_view(),
        name="workout-detail"
    ),
    path("workouts/create/", WorkoutCreateView.as_view(), name="workout-create"),
    path("workouts/<int:pk>/update/", WorkoutUpdateView.as_view(), name="workout-update"),
    path("workouts/<int:pk>/delete/", WorkoutDeleteView.as_view(), name="workout-delete"),
    path(
        "schedules/",
        ScheduleListView.as_view(),
        name="schedule-list"
    ),
    path(
        "schedules/<int:pk>/",
        ScheduleDetailView.as_view(),
        name="schedule-detail"
    ),
    path(
        "schedule/<int:pk>/book/",
        BookingCreateView.as_view(),
        name="schedule-book"
    ),
    path(
        "schedule/<int:pk>/cancel/",
        BookingCancelView.as_view(),
        name="schedule-cancel"
    ),
    path(
        "schedules/create/",
        ScheduleCreateView.as_view(),
        name="schedule-create"
    ),
    path(
        "schedules/<int:pk>/update/",
        ScheduleUpdateView.as_view(),
        name="schedule-update"
    ),
    path(
        "schedules/<int:pk>/delete/",
        ScheduleDeleteView.as_view(),
        name="schedule-delete"
    ),
    path("bookings/", MyBookingView.as_view(), name="my-bookings"),
    path("register/", ClientRegistrationView.as_view(), name="register"),

]
