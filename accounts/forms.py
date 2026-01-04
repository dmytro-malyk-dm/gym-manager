import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import (
    ClientProfile,
    Specialization,
    TrainerProfile
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
                "Phone number must start with +380 " "and contain exactly 9 digits"
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
                user=user, phone_number=self.cleaned_data["phone_number"]
            )

        return user


class TrainerCreationForm(UserCreationForm):
    """Form for admin to create/update trainer accounts"""

    bio = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        required=False,
        help_text="Trainer's biography",
    )

    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        help_text="Trainer's specialization",
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

            self.fields["username"].required = False

            if hasattr(self.instance, "trainer_profile"):
                self.fields["bio"].initial = self.instance.trainer_profile.bio
                self.fields["specialization"].initial = (
                    self.instance.trainer_profile.specialization
                )

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if self.instance and self.instance.pk:
            return self.instance.username

        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if self.instance.pk and not password1 and not password2:
            return password2

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")

        return password2

    def save(self, commit=True):
        """
        Save trainer user and profile.
        Handles both creation and update scenarios.
        Preserves password if not provided during update.
        """

        if self.instance.pk and not self.cleaned_data.get("password1"):
            user = self.instance
            user.email = self.cleaned_data.get("email")
            user.first_name = self.cleaned_data.get("first_name")
            user.last_name = self.cleaned_data.get("last_name")
        else:
            user = super().save(commit=False)

            if not user.pk:
                user.role = "trainer"

        if commit:
            user.save()

            trainer_profile, created = TrainerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "bio": self.cleaned_data.get("bio", ""),
                    "specialization": self.cleaned_data.get("specialization"),
                },
            )

            if not created:
                trainer_profile.bio = self.cleaned_data.get("bio", "")
                trainer_profile.specialization = self.cleaned_data.get("specialization")
                trainer_profile.save()

        return user
