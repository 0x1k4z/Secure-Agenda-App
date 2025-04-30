from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
                    TokenObtainPairView,
                    TokenRefreshView,)

# to map a URL to certain action function in views.

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('challenge/', views.challenge),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]