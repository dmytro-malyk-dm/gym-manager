from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from gym.models import ClientProfile


User = get_user_model()


class ClientRegistrationForm(UserCreationForm):
    """Form for client registration"""

    full_name = forms.CharField(
        max_length=63,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Full name for booking records"
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "client"

        if commit:
            user.save()

            ClientProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                phone_number=self.cleaned_data["phone_number"]
            )

        return user
