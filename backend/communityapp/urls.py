from django.urls import path
from .views import PostCreateAPI, PostDeleteAPI, PostListAPI, PostDetailView, LikePostAPI, UnlikePostAPI, CommentListAPI, CommentCreateAPI

app_name = 'community'

urlpatterns = [
    path('posts/', PostListAPI.as_view(), name='post_list'),
    path('posts/create/', PostCreateAPI.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/delete/', PostDeleteAPI.as_view(), name='post_delete'),
    path('posts/<int:post_id>/like/', LikePostAPI.as_view(), name='like_post'),
    path('posts/<int:post_id>/unlike/', UnlikePostAPI.as_view(), name='unlike_post'),
    path('posts/<int:post_id>/comments/', CommentListAPI.as_view(), name='comment_list'),
    path('posts/<int:post_id>/comments/create/', CommentCreateAPI.as_view(), name='comment_create'),
]