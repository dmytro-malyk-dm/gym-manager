from django import forms
from django.utils import timezone

from gym.models import Schedule, Workout


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


class WorkoutForm(forms.ModelForm):
    """Form for creating/updating workout"""

    class Meta:
        model = Workout
        fields = ["name", "description", "duration_time"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "duration_time": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)