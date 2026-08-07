from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Institution
from .serializers import InstitutionSerializer, CustomTokenObtainPairSerializer


class LoginAPIView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Accepts 'username' and 'password' credentials to issue JWT keys.
    """

    serializer_class = CustomTokenObtainPairSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    """
    CRUD routes for Institutions.
    """
    serializer_class = InstitutionSerializer
    queryset = Institution.objects.all().order_by("name")
    permission_classes = [IsAuthenticated]