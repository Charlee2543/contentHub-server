from django.urls import path
from .views import PostListAPIView,PostDetailAPIView

urlpatterns = [
    path('', PostListAPIView.as_view(), name='post-list'),
    path('<int:article_id>/', PostDetailAPIView.as_view(),name='article-detiail')
]
