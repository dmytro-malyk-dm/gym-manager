import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from gym.models import ClientProfile


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
                "Phone number must start with +380 and contain exactly 9 digits"
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
