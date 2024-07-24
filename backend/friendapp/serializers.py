from rest_framework import serializers
from accountapp.models import Profile

class FriendProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    recent_message = serializers.CharField(read_only=True, required=False)
    unread_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Profile
        fields = ['id', 'nickname', 'profile_pic', 'username', 'bio', 'recent_message', 'unread_count']
