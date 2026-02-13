from django.urls import path
from .views import UserAPIView,UserEditProfile,LoginAPIView,RefreshTokenCookieView, LogoutView


urlpatterns = [
    path('', UserAPIView.as_view(), name='user-list'),
    path('editProfile/', UserEditProfile.as_view(),name='user-edit'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path("token/refresh/", RefreshTokenCookieView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]