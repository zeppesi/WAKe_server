from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import ContentViewSet, RecordViewSet

app_name = 'records'

router = SimpleRouter()
router.register("", RecordViewSet, basename="")
router.register("content", ContentViewSet, basename="content")

urlpatterns = router.urls