from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (CustomTokenObtainPairView, CustomTokenRefreshView,
                    RegisterView, UserDetailView, UserListView, UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
