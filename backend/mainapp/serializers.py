from rest_framework import serializers
from .models import Post,Comment,FollowList,PostImage
from accountapp.models import User, Profile
from django.conf import settings
#from bs4 import BeautifulSoup
import re


class UserInfoSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'profile_pic']

    def get_nickname(self, obj):
        if obj.is_animal:
            return obj.animalprofile.nickname if obj.animalprofile.nickname else obj.username
        return obj.profile.nickname if obj.profile.nickname else obj.username

    def get_profile_pic(self, obj):
        if obj.is_animal:
            if obj.animalprofile.profile_pic_url:
                return f"{obj.animalprofile.profile_pic_url}"
        else:
            if obj.profile.profile_pic:
                return f"{settings.MEDIA_URL}{obj.profile.profile_pic}"
        return f"{settings.MEDIA_URL}default.png"


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image']

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    user = UserInfoSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_id', 'content', 'timestamp', 'images', 'comments_count']

    def create(self, validated_data):
        images_data = self.context.get('images', [])
        user_id = validated_data.pop('user_id', None)
        
        if user_id is None:
            raise serializers.ValidationError("User ID is required to create a post.")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with provided ID does not exist.")

        post = Post.objects.create(user=user, **validated_data)
        
        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)
        
        return post
    
class CommentSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id','post','user','content','timestamp']
        read_only_fields = ['post']

class FollowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowList
        fields = ['id','follower','following']


# 리스트 받아오는용: 계정시리얼라이저 대신

def extract_text_from_html(html_content):
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', html_content)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

class FollowingListSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "nickname", "bio", "profile_pic"]

    def get_nickname(self, obj):
        if obj.is_animal:
            return obj.animalprofile.nickname if obj.animalprofile.nickname else obj.username
        return obj.profile.nickname if obj.profile.nickname else obj.username

    def get_bio(self, obj):
        if obj.is_animal:
            raw_bio = obj.animalprofile.bio
        else:
            raw_bio = obj.profile.bio
        return extract_text_from_html(raw_bio) if raw_bio else ""

    def get_profile_pic(self, obj):
        if obj.is_animal:
            if obj.animalprofile.profile_pic:
                return f"{obj.animalprofile.profile_pic_url}"
        else:
            if obj.profile.profile_pic:
                return f"{settings.MEDIA_URL}{obj.profile.profile_pic}"
        return f"{settings.MEDIA_URL}default.png"
    