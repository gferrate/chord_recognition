from django.contrib import admin
from django.urls import path, include
from backend import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.Home.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
