from django.urls import path
from . import views

urlpatterns = [
    path('create-contact/', views.create_contact, name='create_contact'),
    path('schedule-broadcast/', views.schedule_broadcast, name='schedule_broadcast'),
]