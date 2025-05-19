from django.http import HttpResponse
from django.views.generic import ListView

from portfolio.models import *


class Index(ListView):
    model = UserName
    context_object_name = "data"
    template_name = 'portfolio/index.html'
    extra_context = {
        "title":"Porfolio"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usernames = UserName.objects.all()
        abouts = AboutMe.objects.all()
        skills = Skill.objects.all()
        works = Work.objects.all()
        data = {}
        context['usernames'] = usernames
        context['abouts'] = abouts
        context['skills'] = skills
        context['works'] = works
        context['data'] = data
        return context

    # Shu yerga POST metodini qo'shamiz, Index klassining ichida
    def post(self, request, *args, **kwargs):
        contact = Contact()
        name = request.POST.get('name')
        email = request.POST.get('email')
        massage = request.POST.get('massage')
        contact.name = name
        contact.email = email
        contact.massage = massage
        contact.save()
        return HttpResponse("Contact saved successfully")
