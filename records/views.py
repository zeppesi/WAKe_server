from django.db.models import Q
from rest_framework.generics import ListAPIView

from records.models import Record
from records.serializer import RecordSerializer


class RecordListAPIView(ListAPIView):
    serializer_class = RecordSerializer

    def get_username_filter(self):
        username = self.request.query_params.get('username')
        if not username:
            return Q()
        return Q(profile__name=username)

    def get_queryset(self):
        username_filter = self.get_username_filter()

        records = Record.objects.filter(
            username_filter
        ).select_related(
            'content'
        ).order_by(
            '-created_at'
        )

        return records
