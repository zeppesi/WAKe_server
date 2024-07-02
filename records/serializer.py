from rest_framework import serializers

from records.models import Record, Content


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ('id', 'text',)


class RecordSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    class Meta:
        model = Record
        fields = ('id', 'text', 'created_at', 'updated_at', 'content',)
