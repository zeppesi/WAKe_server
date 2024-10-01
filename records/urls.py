from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import RecordListAPIView, RecordCreateAPIView, ContentViewSet, RecordViewSet, RandomContentAPIView

app_name = 'records'

router = SimpleRouter()
router.register("", RecordViewSet, basename="record")
router.register("content", ContentViewSet, basename="content")

urlpatterns = router.urls

urlpatterns += [
    path("records/list/", RecordListAPIView.as_view(), name="record_list"),
    path("records/create/", RecordCreateAPIView.as_view(), name="record_create"),
    path("contents/random/", RandomContentAPIView.as_view(), name="content_random"),
]
