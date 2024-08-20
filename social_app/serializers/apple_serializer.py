from rest_framework import serializers


class AppleCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()