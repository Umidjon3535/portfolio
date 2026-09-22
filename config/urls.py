from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.urls import re_path

from config import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("portfolio.urls")),
]

# Serve media files in both DEBUG and production (needed for Vercel)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
