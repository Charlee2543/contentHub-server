from django.urls import path
from .views import CommentPost

urlpatterns = [
    path("",CommentPost.as_view())
]
