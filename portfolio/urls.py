from django.urls import path
from portfolio.views import *

urlpatterns = [
    path("", Index.as_view(), name="index"),

]