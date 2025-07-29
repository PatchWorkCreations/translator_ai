from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('translate/', views.ai_translate, name='ai_translate'),
    
]
