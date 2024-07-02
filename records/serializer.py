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


class RecordCreateSerializer(serializers.Serializer):
    content_id = serializers.IntegerField()
    username = serializers.CharField(max_length=20)
    text = serializers.CharField(max_length=100, allow_blank=True, allow_null=True)


"""
    Swagger Query param serializers
"""


class RandomContentQuerySerializer(serializers.Serializer):
    prev = serializers.IntegerField(required=False, help_text='이전 content id')


class RecordListQuerySerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, required=False)
