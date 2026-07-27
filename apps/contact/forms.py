from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Votre nom")}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": _("Votre courriel")}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Votre téléphone (optionnel)")}
            ),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Objet")}),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 6, "placeholder": _("Votre message")}
            ),
        }
