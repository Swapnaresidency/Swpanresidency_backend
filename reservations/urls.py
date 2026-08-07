from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckInViewSet, CheckOutViewSet

router = DefaultRouter()

router.register(r'checkins', CheckInViewSet)
router.register(r'checkouts', CheckOutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]