from django.urls import path
from . import views
from .views import get_analytics, dashboard

urlpatterns = [
    path('create-contact/', views.create_contact, name='create_contact'),
    path('schedule-broadcast/', views.schedule_broadcast, name='schedule_broadcast'),
    path('analytics/', get_analytics, name='get_analytics'),
]