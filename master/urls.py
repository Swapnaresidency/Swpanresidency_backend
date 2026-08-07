from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomTypeViewSet, RoomViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'room-types', RoomTypeViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
