from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstitutionViewSet, LoginAPIView

router = DefaultRouter()
router.register(r"institutions", InstitutionViewSet, basename="institutions")

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name='user_login'),
    path("", include(router.urls)),
    
    # path('api/auth/', include('dj_rest_auth.urls')), # This provides /api/auth/login/
    # path('api/auth/', include('djoser.urls.authtoken')), 
]