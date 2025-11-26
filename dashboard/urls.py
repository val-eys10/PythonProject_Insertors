from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('add/', views.add_record, name='add_record'),
    path('reset/', views.reset_data, name='reset_data'),
]
