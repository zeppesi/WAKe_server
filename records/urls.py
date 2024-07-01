from django.urls import path, include
from rest_framework.routers import SimpleRouter

from users.views import RecordViewSet

app_name = 'records'

router = SimpleRouter()
router.register('', RecordViewSet, 'records')

urlpatterns = [
    path('', include((router.urls, 'records'))),
]
