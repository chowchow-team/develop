from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Notification
from django.shortcuts import get_object_or_404


User = get_user_model()
class DeleteDMNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_username):
        user = request.user
        friend = User.objects.get(username=friend_username)

        notifications = Notification.objects.filter(sender=friend, receiver=user, user_has_seen=False)
        notifications.delete()
        
        return Response({"message": "Notifications marked as seen"})

class CheckAnyNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(receiver=user, user_has_seen=False)
        if notifications.exists():
            return Response({"message": "You have notifications"})
        return Response({"message": "You have no notifications"})
    
class RemoveBothNotificationAPI(APIView): # 채팅방 삭제 시 알림 삭제
    permission_classes = [IsAuthenticated]

    def delete(self, request, friend_username, format=None):
        user = request.user
        friend = get_object_or_404(User, username=friend_username)

        my_notifications = Notification.objects.filter(sender=friend, receiver=user, user_has_seen=False)
        my_notifications.delete()
        ur_notifications = Notification.objects.filter(sender=user, receiver=friend, user_has_seen=False)
        ur_notifications.delete()

        return Response({"message": "Notifications deleted"})