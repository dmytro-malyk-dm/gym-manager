import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone

from gym.models import (
    ClientProfile,
    Schedule,
    Workout, Specialization, TrainerProfile
)

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
        if self.instance.pk:
            old_start = Schedule.objects.get(pk=self.instance.pk).start_time
            now = timezone.now()

            if old_start <= now:
                raise forms.ValidationError(
                    "Cannot edit schedule that has already started."
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


class TrainerCreationForm(UserCreationForm):
    """Form for admin to create/update trainer accounts"""

    bio = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        required=False,
        help_text="Trainer's biography"
    )

    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        help_text="Trainer's specialization"
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

    def __init__(self, *args, **kwargs):
        is_update = kwargs.get("instance") is not None
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

        if is_update:
            self.fields["password1"].required = False
            self.fields["password2"].required = False
            self.fields["password1"].help_text = "Leave blank to keep current password"

            if hasattr(self.instance, "trainer_profile"):
                self.fields["bio"].initial = self.instance.trainer_profile.bio
                self.fields["specialization"].initial = self.instance.trainer_profile.specialization

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not password1 and not password2:
            return password2

        return super().clean_password2()

    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.pk:
            user.role = "trainer"

        if user.pk and self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            trainer_profile, created = TrainerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "bio": self.cleaned_data.get("bio", ""),
                    "specialization": self.cleaned_data.get("specialization")
                }
            )

            if not created:
                trainer_profile.bio = self.cleaned_data.get("bio", "")
                trainer_profile.specialization = self.cleaned_data.get("specialization")
                trainer_profile.save()

        return user
