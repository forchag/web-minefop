from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ContactForm
from .models import ContactInfo


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            try:
                send_mail(
                    subject=f"[MINEFOP - Contact] {contact_message.subject}",
                    message=(
                        f"Nom : {contact_message.name}\n"
                        f"Courriel : {contact_message.email}\n"
                        f"Téléphone : {contact_message.phone}\n\n"
                        f"{contact_message.message}"
                    ),
                    from_email=settings.CONTACT_RECIPIENT_EMAIL,
                    recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(
                request,
                _("Votre message a bien été envoyé. Nous vous répondrons dans les meilleurs délais."),
            )
            return redirect("contact:contact")
    else:
        form = ContactForm()

    context = {"form": form, "info": ContactInfo.load()}
    return render(request, "contact/contact.html", context)
