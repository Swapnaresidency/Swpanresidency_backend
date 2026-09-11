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
        extra_kwargs = {
            "email": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "gst": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

    def validate_email(self, value):
        if value in ("", None):
            return None
        return value

    def validate_gst(self, value):
        if value in ("", None):
            return None
        return value.strip()