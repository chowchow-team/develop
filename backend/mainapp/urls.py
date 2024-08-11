from django.urls import path
from .views import PostRecentAPIView, PostFollowAPIView, PostControlAPIView, CommentControlAPIView, FollowRecommandAPIView,FollowRequestAPIView,FollowerListAPIView,FollowingListAPIView,UnfollowRequestAPIView,FollowCheckAPIView,UserPostListView,LikePostAPIView,UserLikedPostsAPIView

app_name = 'main'

urlpatterns = [
    path('', PostRecentAPIView.as_view(),name='recommand_list'),
    path('post/follow/',PostFollowAPIView.as_view(),name='follow_list'),
    path('comment/',CommentControlAPIView.as_view(),name='content'),
    path('follow/',FollowRecommandAPIView.as_view(),name='write_page'),
    path('follow/request/',FollowRequestAPIView.as_view(),name='follow_request'),
    path('follower/list/',FollowerListAPIView.as_view(),name='followers'),
    path('following/list/',FollowingListAPIView.as_view(),name='followings'),
    path('unfollow/request/',UnfollowRequestAPIView.as_view(),name='unfollow'),
    path('post/',PostControlAPIView.as_view(),name='post'),
    path('following/check/',FollowCheckAPIView.as_view(),name='follow_check'),
    path('post/<str:username>/', UserPostListView.as_view(), name='user-post-list'),
    path('like/', LikePostAPIView.as_view(), name='like-post'),
    path('liked-posts/', UserLikedPostsAPIView.as_view(), name='user-liked-posts'),

]