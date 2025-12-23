import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone

from gym.models import ClientProfile, Schedule, Workout

User = get_user_model()


class ClientRegistrationForm(UserCreationForm):
    """Form for client registration"""

    phone_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+380XXXXXXXXX",
                "value": "+380",
            }
        ),
        help_text="Phone number must start with +380 and contain 9 digits",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]

        pattern = r"^\+380\d{9}$"
        if not re.match(pattern, phone):
            raise forms.ValidationError(
                "Phone number must start with +380 "
                "and contain exactly 9 digits"
            )

        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "client"

        if commit:
            user.save()

            ClientProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data["phone_number"]
            )

        return user


class ScheduleForm(forms.ModelForm):
    """Form for creating/updating schedule"""

    class Meta:
        model = Schedule
        fields = ["workout", "start_time", "capacity"]
        widgets = {
            "workout": forms.Select(attrs={"class": "form-control"}),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.role == "trainer":
                self.fields["workout"].queryset = Workout.objects.filter(
                    trainer__user=self.user
                )
            elif self.user.role == "admin":
                self.fields["workout"].queryset = Workout.objects.all()

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")

        if start_time and start_time < timezone.now():
            raise forms.ValidationError(
                "Cannot create schedule in the past."
            )

        return start_time


class ScheduleSearchForm(forms.Form):
    """Form for searching schedule"""
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "Select date"
            }
        )
    )
    workout_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by workout name..."
            }
        )
    )
