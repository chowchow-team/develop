from django.urls import path
from .views import MessageListAPI, RemoveMessageAPI

app_name = 'chatapp'

urlpatterns = [
    path('dm/<str:friend_username>/', MessageListAPI.as_view(), name='dm_detail'),
    path('remove-messages/<str:friend_username>/', RemoveMessageAPI.as_view(), name='remove_messages'),
    #path('dm/active-status/', DMActiveStatusAPI.as_view(), name='dm_active_status'),
]