from django.urls import path
from .views import CommentPost, CommentByArticleView, CommentReplyView

urlpatterns = [
    path("",CommentPost.as_view(), name='comment-list-create'),
    # GET /commentPost/by-article/
    path('by-article/', CommentByArticleView.as_view(), name='comments-by-article'),
    
    # POST /commentPost/<int:comment_id>/reply/
    path('<int:comment_id>/reply/', CommentReplyView.as_view(), name='comment-reply'),
    ]


