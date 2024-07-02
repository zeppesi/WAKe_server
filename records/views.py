from django.db.models import Q
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from records.models import Record, Content
from records.serializer import RecordSerializer, ContentSerializer, RecordCreateSerializer
from users.models import Profile


class RandomContentAPIView(GenericAPIView):
    serializer_class = ContentSerializer

    def get_prev_filter(self) -> Q:
        prev = self.request.query_params.get('prev')
        if not prev:
            return Q()
        return ~Q(id=int(prev))

    def get(self, request: Request):
        prev_filter = self.get_prev_filter()
        queryset = Content.objects.filter(
            prev_filter
        ).order_by(
            '?'
        ).first()

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class RecordCreateAPIView(CreateAPIView):
    serializer_class = RecordCreateSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer: RecordCreateSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        content_id = serializer.validated_data.get('content_id')
        text = serializer.validated_data.get('text')

        profile = Profile.objects.get(name=username)

        record = Record.objects.create(
            content_id=content_id,
            profile=profile,
            text=text
        )

        record_serializer = RecordSerializer(record)

        return Response(record_serializer.data)


class RecordListAPIView(ListAPIView):
    serializer_class = RecordSerializer

    def get_username_filter(self) -> Q:
        username = self.request.query_params.get('username')
        if not username:
            return Q()
        return Q(profile__name=username)

    def get_queryset(self):
        username_filter = self.get_username_filter()

        queryset = Record.objects.filter(
            username_filter
        ).select_related(
            'content'
        ).order_by(
            '-created_at'
        )

        return queryset
