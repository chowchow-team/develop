from django.urls import path
from .views import PostRecentAPIView, PostFollowAPIView, PostControlAPIView, CommentControlAPIView, FollowRecommandAPIView,FollowRequestAPIView,FollowListAPIView

app_name = 'main'

urlpatterns = [
    path('', PostRecentAPIView.as_view(),name='recommand_list'),
    path('post/follow',PostFollowAPIView.as_view(),name='follow_list'),
    path('comment/<int:post_id>/',CommentControlAPIView.as_view(),name='content'),
    path('follow/',FollowRecommandAPIView.as_view(),name='write_page'),
    path('follow/request/',FollowRequestAPIView.as_view(),name='follow_request'),
    path('follow/list/',FollowListAPIView.as_view(),name='all_follow'),
    path('post/',PostControlAPIView.as_view(),name='post'),
]