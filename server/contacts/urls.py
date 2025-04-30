from django.urls import path
from . import views

# to map a URL to certain action function in views.

urlpatterns = [
    path('list/', views.myContacts),
    path('add/', views.addContact),
    path('accept/', views.acceptContact),
    path('remove/', views.removeContact),
    path('pending/', views.pendingContacts),
]