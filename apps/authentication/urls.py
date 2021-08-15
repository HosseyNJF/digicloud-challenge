from django.urls import path

from apps.authentication.views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
]
