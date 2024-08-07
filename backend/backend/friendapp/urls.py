from django.urls import path
from .views import FriendListAPI, RemoveFriendAPI

app_name = 'friends'

urlpatterns = [
    path('list/', FriendListAPI.as_view(), name='friend_list'),
    path('remove/<str:friend_username>/', RemoveFriendAPI.as_view(), name='remove_friend'),
]