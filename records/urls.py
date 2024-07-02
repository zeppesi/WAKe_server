from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import RecordListAPIView, RandomContentAPIView, RecordCreateAPIView

app_name = 'records'

router = SimpleRouter()

urlpatterns = [
    path("records/list/", RecordListAPIView.as_view(), name="record_list"),
    path("records/create/", RecordCreateAPIView.as_view(), name="record_create"),
    path("contents/random/", RandomContentAPIView.as_view(), name="content_random"),
]
