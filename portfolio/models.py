from django.db import models

# Create your models here.

class  UserName(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "UserName"
        verbose_name_plural = "UserNames"

class  AboutMe(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to="images/", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "AboutMe"
        verbose_name_plural = "AboutMes"

class  Skill(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    progress = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
class  Work(models.Model):
    title = models.CharField(max_length=100)
    link = models.URLField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to="images/", blank=True, null=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Works"

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()  # textarea uchun

    def __str__(self):
        return f"{self.name} - {self.email}"






