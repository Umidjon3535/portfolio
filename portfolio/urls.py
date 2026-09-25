from django.urls import path

from portfolio.views import Index

urlpatterns = [
    path("", Index.as_view(), name="index"),
]
