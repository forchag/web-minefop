from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import CandidateProfile

User = get_user_model()


class CandidateAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CandidateSignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_("Prénom"), max_length=150)
    last_name = forms.CharField(label=_("Nom"), max_length=150)
    email = forms.EmailField(label=_("Courriel"))
    phone = forms.CharField(label=_("Téléphone"), max_length=50, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Un compte existe déjà avec ce courriel."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            CandidateProfile.objects.create(user=user, phone=self.cleaned_data.get("phone", ""))
        return user


class JoinProgramForm(forms.Form):
    access_code = forms.CharField(
        label=_("Code d'accès de la formation"),
        max_length=12,
        widget=forms.TextInput(attrs={"class": "form-control text-uppercase", "placeholder": _("Ex : AB12CD34")}),
    )

    def clean_access_code(self):
        return self.cleaned_data["access_code"].strip().upper()
