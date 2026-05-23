from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import PlayerSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class PlayerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user
