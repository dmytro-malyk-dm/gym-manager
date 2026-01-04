from django.urls import path

from accounts.views import (
    ClientRegistrationView,
    TrainerCreateView,
    TrainerUpdateView,
    TrainerListView,
    TrainerDetailView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", ClientRegistrationView.as_view(), name="register"),
    path("trainers/", TrainerListView.as_view(), name="trainer-list"),
    path("trainers/<int:pk>/", TrainerDetailView.as_view(), name="trainer-detail"),
    path("trainers/create/", TrainerCreateView.as_view(), name="trainer-create"),
    path(
        "trainers/<int:pk>/update/", TrainerUpdateView.as_view(), name="trainer-update"
    ),
]
