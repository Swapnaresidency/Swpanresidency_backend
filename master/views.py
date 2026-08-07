from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import RoomType, Room
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


class RoomTypeViewSet(viewsets.ModelViewSet):
    permission_classes  = [IsAuthenticated]
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    parser_classes = (MultiPartParser, FormParser)