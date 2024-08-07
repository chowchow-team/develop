from rest_framework import serializers
from .models import Post,Comment,FollowList

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','user','content','timestamp','title']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id','post','user','content','timestamp']
        read_only_fields = ['post']
class FollowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowList
        fields = ['id','follower','following']
    