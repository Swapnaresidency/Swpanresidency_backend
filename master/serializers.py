from rest_framework import serializers
from .models import *


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(
        source="room_type.category",
        read_only=True
    )

    class Meta:
        model = Room
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"