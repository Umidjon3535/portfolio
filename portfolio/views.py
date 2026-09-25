import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db import DatabaseError
from django.shortcuts import redirect
from django.views.generic import TemplateView

from portfolio.forms import ContactForm
from portfolio.models import AboutMe, Skill, UserName, Work

logger = logging.getLogger(__name__)


def send_contact_email(data):
    if not settings.EMAIL_HOST_PASSWORD:
        return False
    email = EmailMessage(
        subject=f"Portfolio: {data['name']} dan yangi xabar",
        body=f"Ism: {data['name']}\nEmail: {data['email']}\n\n{data['message']}",
        to=[settings.CONTACT_EMAIL],
        reply_to=[data['email']],
    )
    try:
        email.send()
    except Exception:
        logger.exception("Kontakt xabarini emailga yuborib bo'lmadi")
        return False
    return True


class Index(TemplateView):
    template_name = 'portfolio/index.html'
    extra_context = {
        "title": "Portfolio"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usernames'] = UserName.objects.all()
        context['abouts'] = AboutMe.objects.all()
        context['skills'] = Skill.objects.all()
        context['works'] = Work.objects.all()
        context.setdefault('form', ContactForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        try:
            form.save()
            saved = True
        except DatabaseError:
            # Vercel'da SQLite faqat o'qish uchun, yozib bo'lmaydi
            logger.exception("Kontakt xabarini bazaga saqlab bo'lmadi")
            saved = False
        sent = send_contact_email(form.cleaned_data)

        if saved or sent:
            messages.success(request, "Xabaringiz uchun rahmat! Tez orada javob beraman.")
        else:
            messages.error(request, "Xabarni yuborib bo'lmadi. Iltimos, keyinroq urinib ko'ring.")
        return redirect('/#contact')
