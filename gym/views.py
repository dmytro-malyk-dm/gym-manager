from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView

from gym.models import TrainerProfile, Specialization, ClientProfile, Workout, Schedule


class HomeTemplateView(TemplateView):
    template_name ="gym/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["num_trainers"] = TrainerProfile.objects.count()
        context["num_specialization"] = Specialization.objects.count()
        context["num_clients"] = ClientProfile.objects.count()
        num_visit = self.request.session.get("num_visit", 0) + 1
        self.request.session["num_visit"] = num_visit
        context["num_visit"] = num_visit

        return context

class TrainerListView(generic.ListView):
    model = TrainerProfile
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).order_by("user__first_name")
    paginate_by = 5


class TrainerDetailView(generic.DetailView):
    model = TrainerProfile
    context_object_name = "trainers"
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).prefetch_related("workouts")


class WorkoutListView(generic.ListView):
    model = Workout
    queryset = Workout.objects.select_related(
        "trainer",
        "trainer__user"
    ).order_by("name")
    paginate_by = 5


class WorkoutDetailView(generic.DetailView):
    model = Workout
    queryset = Workout.objects.select_related(
        "trainer", "trainer__user"
    ).prefetch_related("schedules")


class ScheduleListView(generic.ListView):
    model = Schedule
    queryset = Schedule.objects.select_related(
        "workout",
        "workout__trainer",
        "workout__trainer__user"
    )




