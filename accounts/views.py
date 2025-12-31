from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from accounts.forms import ClientRegistrationForm, TrainerCreationForm
from accounts.models import TrainerProfile, User


class ClientRegistrationView(generic.CreateView):
    template_name = "accounts/register.html"
    form_class = ClientRegistrationForm
    success_url = reverse_lazy("login")

    def get_success_url(self):
        messages.success(self.request, "Registration successful! Please login.")
        return super().get_success_url()


class TrainerListView(LoginRequiredMixin, generic.ListView):
    model = TrainerProfile
    context_object_name = "trainers"
    queryset = TrainerProfile.objects.select_related("user", "specialization").order_by(
        "user__first_name"
    )
    paginate_by = 9


class TrainerDetailView(LoginRequiredMixin, generic.DetailView):
    model = TrainerProfile
    context_object_name = "trainer"
    queryset = TrainerProfile.objects.select_related(
        "user", "specialization"
    ).prefetch_related("workouts")


class TrainerCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    """Admin can create trainer accounts"""

    model = User
    form_class = TrainerCreationForm
    success_url = reverse_lazy("accounts:trainer-list")
    template_name = "accounts/trainerprofile_form.html"

    def test_func(self):
        """Check if user has admin role"""
        return self.request.user.role == "admin"

    def handle_no_permission(self):
        messages.error(self.request, "Only admins can access this page.")
        return redirect("accounts:trainer-list")

    def form_valid(self, form):
        messages.success(
            self.request, f"Trainer {form.instance.username} created successfully!"
        )
        return super().form_valid(form)


class TrainerUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """Admin can edit trainer profiles"""

    model = User
    form_class = TrainerCreationForm
    template_name = "accounts/trainerprofile_form.html"

    def test_func(self):
        """Check if user can edit this trainer profile"""
        user = self.request.user
        if user.role == "admin":
            return True
        if user.role == "trainer":
            trainer_profile = get_object_or_404(TrainerProfile, pk=self.kwargs["pk"])
            return trainer_profile.user == user
        return False

    def get_object(self):
        trainer_profile = get_object_or_404(TrainerProfile, pk=self.kwargs["pk"])
        return trainer_profile.user

    def get_success_url(self):
        trainer_profile = TrainerProfile.objects.get(user=self.object)
        return reverse_lazy(
            "accounts:trainer-detail", kwargs={"pk": trainer_profile.pk}
        )

    def form_valid(self, form):
        messages.success(
            self.request, f"Trainer {form.instance.username} updated successfully!"
        )
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this profile.")
        return redirect("accounts:trainer-list")
