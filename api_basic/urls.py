from django.urls import path, include
from .views import  FilesAPIView
from rest_framework.routers import DefaultRouter



urlpatterns = [

    path('files/', FilesAPIView.as_view()),
]