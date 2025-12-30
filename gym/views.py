from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib import messages

from gym.forms import (
    ClientRegistrationForm,
    ScheduleSearchForm,
    ScheduleForm
)
from gym.models import (
    TrainerProfile,
    Specialization,
    ClientProfile,
    Workout,
    Schedule,
    Booking
)


class HomeTemplateView(TemplateView):
    template_name = "gym/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["num_trainers"] = TrainerProfile.objects.count()
        context["num_specialization"] = Specialization.objects.count()
        context["num_clients"] = ClientProfile.objects.count()
        num_visit = self.request.session.get("num_visit", 0) + 1
        self.request.session["num_visit"] = num_visit
        context["num_visit"] = num_visit

        return context


class TrainerListView(LoginRequiredMixin, generic.ListView):
    model = TrainerProfile
    context_object_name = "trainers"
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).order_by("user__first_name")
    paginate_by = 9


class TrainerDetailView(LoginRequiredMixin, generic.DetailView):
    model = TrainerProfile
    context_object_name = "trainer"
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).prefetch_related("workouts")


class WorkoutListView(LoginRequiredMixin, generic.ListView):
    model = Workout
    queryset = Workout.objects.select_related(
        "trainer",
        "trainer__user"
    ).order_by("name")
    paginate_by = 9


class WorkoutDetailView(LoginRequiredMixin, generic.DetailView):
    model = Workout
    queryset = Workout.objects.select_related(
        "trainer", "trainer__user", "trainer__specialization"
    ).prefetch_related("schedules", "schedules__bookings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming_schedules"] = self.object.schedules.filter(
            start_time__gte=timezone.now()
        ).order_by("start_time")
        return context


class TrainerOrAdminMixin(UserPassesTestMixin):
    """Mixin to restrict access to trainers and admins only"""

    def test_func(self):
        return self.request.user.role in ["trainer", "admin"]

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Only trainers and admins can access this page."
        )
        return redirect("gym:schedule-list")


class ScheduleListView(LoginRequiredMixin, generic.ListView):
    model = Schedule
    paginate_by = 12

    def get_queryset(self):
        queryset = Schedule.objects.filter(
            start_time__gte=timezone.now()
        ).select_related(
            "workout",
            "workout__trainer",
            "workout__trainer__user"
        ).prefetch_related("bookings").order_by("start_time")

        form = ScheduleSearchForm(self.request.GET)
        if form.is_valid():
            date = form.cleaned_data.get("date")
            workout_name = form.cleaned_data.get("workout_name")

            if date:
                queryset = queryset.filter(start_time__date=date)

            if workout_name:
                queryset = queryset.filter(
                    workout__name__icontains=workout_name
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ScheduleSearchForm(
            initial={
                "date": self.request.GET.get("date", ""),
                "workout_name": self.request.GET.get("workout_name", ""),
            }
        )
        context["can_manage"] = self.request.user.role in ["trainer", "admin"]
        return context


class ScheduleDetailView(LoginRequiredMixin, generic.DetailView):
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
        ).exists()

        context["available_spots"] = (schedule.capacity
                                      - schedule.bookings.count())
        context["is_full"] = context["available_spots"] <= 0
        context["can_book"] = (schedule.start_time > timezone.now()
                               and user.role == "client")
        if user.role in ["admin", "trainer"]:
            context["show_participants"] = True
            context["participants"] = schedule.bookings.select_related(
                "client", "client__client_profile"
            )
            context["can_manage"] = True

        return context


class ScheduleCreateView(
    LoginRequiredMixin,
    TrainerOrAdminMixin,
    generic.CreateView
):
    """Create new schedule (trainers and admins only)"""
    model = Schedule
    form_class = ScheduleForm
    success_url = reverse_lazy("gym:schedule-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Schedule for {form.instance.workout.name} created successfully!"
        )
        return super().form_valid(form)


class ScheduleUpdateView(
    LoginRequiredMixin,
    TrainerOrAdminMixin,
    generic.UpdateView
):
    """Update schedule (trainers and admins only)"""
    model = Schedule
    form_class = ScheduleForm
    success_url = reverse_lazy("gym:schedule-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        if not super().test_func():
            return False

        if self.request.user.role == "trainer":
            schedule = self.get_object()
            return schedule.workout.trainer.user == self.request.user

        return True

    def form_valid(self, form):
        messages.success(
            self.request,
            "Schedule updated successfully!"
        )
        return super().form_valid(form)


class ScheduleDeleteView(
    LoginRequiredMixin,
    TrainerOrAdminMixin,
    generic.DeleteView
):
    """Delete schedule (trainers and admins only)"""
    model = Schedule
    success_url = reverse_lazy("gym:schedule-list")

    def test_func(self):
        if not super().test_func():
            return False

        if self.request.user.role == "trainer":
            schedule = self.get_object()
            return schedule.workout.trainer.user == self.request.user

        return True

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Schedule deleted successfully!")
        return super().delete(request, *args, **kwargs)


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
    success_url = reverse_lazy("login")

    def get_success_url(self):
        messages.success(
            self.request,
            "Registration successful! Please login."
        )
        return super().get_success_url()


class MyBookingView(LoginRequiredMixin, generic.ListView):
    model = Booking
    template_name = "gym/my_bookings.html"

    def get_queryset(self):
        return Booking.objects.filter(
            client=self.request.user
        ).select_related(
            "schedule",
            "schedule__workout",
            "schedule__workout__trainer__user"
        ).order_by("-schedule__start_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context
