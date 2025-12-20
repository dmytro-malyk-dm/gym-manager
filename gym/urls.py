from django.urls import path

from gym.views import HomeTemplateView

app_name = "gym"

urlpatterns = [
    path("", HomeTemplateView.as_view(), name="index"),
]