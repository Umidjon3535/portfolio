from django.contrib import admin

from portfolio.models import AboutMe, Contact, Skill, UserName, Work

admin.site.register(UserName)
admin.site.register(AboutMe)
admin.site.register(Work)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "progress")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message")
    search_fields = ("name", "email", "message")
