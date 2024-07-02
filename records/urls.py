from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import RecordListAPIView, RandomContentAPIView

app_name = 'records'

router = SimpleRouter()

urlpatterns = [
    path("records/", RecordListAPIView.as_view(), name="record_list"),
    path("contents/random/", RandomContentAPIView.as_view(), name="random_content"),
]
