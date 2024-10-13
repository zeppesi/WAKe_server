from django.urls import path, include
from rest_framework.routers import SimpleRouter

from accounts.views import LoginViewSet

app_name = 'accounts'

router = SimpleRouter()
router.register('login', LoginViewSet, basename='login')

urlpatterns = router.urls
