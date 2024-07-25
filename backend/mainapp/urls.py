from django.urls import path
from .views import PostRecentAPIView, PostFollowAPIView, PostControlAPIView, CommentControlAPIView, FollowRecommandAPIView

app_name = 'main'

urlpatterns = [
    path('', PostRecentAPIView.as_view(),name='recommand_list'),
    path('post/follow',PostFollowAPIView.as_view(),name='follow_list'),
    path('comment/',CommentControlAPIView.as_view(),name='content'),
    path('follow/',FollowRecommandAPIView.as_view(),name='write_page'),
]