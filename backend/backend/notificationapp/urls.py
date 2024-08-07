from django.urls import path
from .views import DeleteDMNotificationAPI, CheckAnyNotificationAPI, RemoveBothNotificationAPI

app_name = 'notifications'

urlpatterns = [
    path('delete/dm/<str:friend_username>/', DeleteDMNotificationAPI.as_view(), name='delete_dm_notification'),
    path('delete-both/dm/<str:friend_username>/', RemoveBothNotificationAPI.as_view(), name='delete_both_notification'),
    path('check-notification/', CheckAnyNotificationAPI.as_view(), name='check_any_notification'),
]