from django.urls import path, include
from rest_framework.routers import SimpleRouter

from records.views import RecordListAPIView

app_name = 'records'

router = SimpleRouter()
# router.register('', RecordViewSet, 'records')

urlpatterns = [
    # path('', include((router.urls, 'records'))),
    path("records/", RecordListAPIView.as_view(), name="record_list"),
]
