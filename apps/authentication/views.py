from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.authentication.models import User
from apps.authentication.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
