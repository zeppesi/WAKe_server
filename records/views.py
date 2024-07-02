from django.db.models import Q
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from records.models import Record, Content
from records.serializer import RecordSerializer, ContentSerializer


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
