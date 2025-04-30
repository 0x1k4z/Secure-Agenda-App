from django.urls import path
from . import views

# to map a URL to certain action function in views.

urlpatterns = [
    path('list/', views.myEvents),
    path('invitations/', views.invitedEvents),
    path('create/', views.createEvent),
    path('modify/', views.modifyEvent),
    path('remove/', views.removeEvent),
]