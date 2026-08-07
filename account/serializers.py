from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Institution

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"   
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Overriding the username field configuration since your identifier is 'code'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()

    def validate(self, attrs):
        # Authenticates against Django's default USERNAME_FIELD ("username")
        data = super().validate(attrs)
        user = self.user

        # Inject User model fields into the JWT response payload
        data['status'] = True
        data['message'] = "Login successful"
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mobile': user.mobile,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
        }

        return data