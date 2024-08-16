from rest_framework import serializers
from .models import Post,Comment,FollowList,PostImage,Like
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
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    file = serializers.FileField(required=False)

    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    def get_like_count(self, obj):
        return obj.like_count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_id', 'content', 'timestamp', 'images', 'comments_count', 'view_count', 'like_count', 'is_liked', 'file']

    def create(self, validated_data):
        file = self.context.get('file', None)
        images_data = self.context.get('images', [])
        user_id = validated_data.pop('user_id', None)
        
        if user_id is None:
            raise serializers.ValidationError("게시물을 생성하려면 사용자 ID가 필요합니다.")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("제공된 ID를 가진 사용자가 존재하지 않습니다.")

        post = Post.objects.create(user=user, **validated_data)

        if file:
            try:
                post.save_with_file(file)
            except ValidationError as e:
                post.delete()
                raise serializers.ValidationError(f"파일 저장 중 오류 발생: {str(e)}")
            except Exception as e:
                post.delete()
                raise serializers.ValidationError(f"파일 처리 중 예기치 않은 오류 발생: {str(e)}")

        for image_data in images_data:
            try:
                PostImage.objects.create(post=post, image=image_data)
            except Exception as e:
                post.delete()
                raise serializers.ValidationError(f"이미지 저장 중 오류 발생: {str(e)}")
        
        return post
    
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

    
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
            return obj.animalprofile.profile_pic_url
        else:
            if obj.profile.profile_pic:
                return f"{settings.MEDIA_URL}{obj.profile.profile_pic}"
        return f"{settings.MEDIA_URL}default.png"
    