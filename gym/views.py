from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib import messages

from gym.forms import ClientRegistrationForm
from gym.models import TrainerProfile, Specialization, ClientProfile, Workout, Schedule, Booking


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
    context_object_name = "trainers"
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).order_by("user__first_name")
    paginate_by = 5


class TrainerDetailView(generic.DetailView):
    model = TrainerProfile
    context_object_name = "trainer"
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
    ).order_by("start_time")

class ScheduleDetailView(generic.DetailView):
    model = Schedule
    queryset = Schedule.objects.select_related(
        "workout",
        "workout__trainer",
        "workout__trainer__user",
        "workout__trainer__specialization"
    ).prefetch_related("bookings", "bookings__client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = self.object
        user = self.request.user

        context["is_booked"] = schedule.bookings.filter(
            client=user
        )

        context["available_spots"] = schedule.capacity - schedule.bookings.count()
        context["is_full"] = context["available_spots"] <= 0
        context["can_book"] = schedule.start_time > timezone.now()
        if user.role in ["admin", "trainer"]:
            context["show_participants"] = True
            context["participants"] = schedule.bookings.select_related(
                "client"
            )
        return context

class BookingCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        user = request.user

        if user.role != "client":
            messages.error(request, "Only clients can book workouts.")
            return redirect("gym:schedule-detail", pk=pk)

        if schedule.start_time <= timezone.now():
            messages.error(request, "This workout has already started.")
            return redirect("gym:schedule-detail", pk=pk)

        if schedule.bookings.count() >= schedule.capacity:
            messages.error(request, "No available spots.")
            return redirect("gym:schedule-detail", pk=pk)

        if schedule.bookings.filter(client=user).exists():
            messages.warning(request, "You are already booked.")
            return redirect("gym:schedule-detail", pk=pk)

        overlapping = Schedule.objects.filter(
            start_time=schedule.start_time,
            bookings__client=user
        ).exists()

        if overlapping:
            messages.error(request, "You already have a workout at this time.")
            return redirect("gym:schedule-detail", pk=pk)

        Booking.objects.create(
            schedule=schedule,
            client=user
        )

        messages.success(request, "Successfully booked!")
        return redirect("gym:schedule-detail", pk=pk)


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        user = request.user

        Booking.objects.filter(
            schedule=schedule,
            client=user
        ).delete()

        messages.success(request, "Booking canceled.")
        return redirect("gym:schedule-detail", pk=pk)



class ClientRegistrationView(generic.CreateView):
    template_name = "gym/register.html"
    form_class = ClientRegistrationForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
