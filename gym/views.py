from django.shortcuts import render
from django.views.generic import TemplateView

from gym.models import TrainerProfile, Specialization, ClientProfile


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



