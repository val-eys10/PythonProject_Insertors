from django.shortcuts import redirect
from django.urls import path
from . import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
]