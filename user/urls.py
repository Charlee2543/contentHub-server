from django.urls import path
from .views import UserAPIView,UserEditProfile,LoginAPIView

urlpatterns = [
    path('', UserAPIView.as_view(), name='user-list'),
    path('<uuid:pk>/', UserEditProfile.as_view(),name='user-edit'),
    path('login/', LoginAPIView.as_view(), name='login'),
]