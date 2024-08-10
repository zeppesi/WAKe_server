from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'created_at',)


class LogoutSerializer(serializers.Serializer):
    pass