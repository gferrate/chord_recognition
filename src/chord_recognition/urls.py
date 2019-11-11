from django.contrib import admin
from django.urls import path, include
from backend import views

urlpatterns = [
    path('', include('backend.urls')),
    path('admin/', admin.site.urls),
]
