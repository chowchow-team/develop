from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import User, Profile, AnimalProfile
import json

from PIL import Image
from django.core.files.base import ContentFile
import io
import os
from django.conf import settings

class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email", "password","id"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # 사용자를 비활성화 상태로 설정
        user.save()
        return user
    

def save_image_as_png(image, user):
    """
    이미지를 PNG 형식으로 변환하고 저장하는 함수.
    """
    output = io.BytesIO()
    # RGB 모드로 변경하여 PNG 저장을 보장
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(output, format='PNG', quality=80)
    image_data = output.getvalue()
    file_name = f"{user.username}.png"
    file_path = os.path.join('profile_pics', file_name)
    # 기존 파일 삭제 로직을 함수 내부에 포함
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(full_file_path):
        os.remove(full_file_path)
    # ContentFile을 사용하여 메모리상의 이미지 데이터를 저장
    user.profile_pic.save(file_name, ContentFile(image_data), save=False)


'''
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['nickname', 'profile_pic', 'bio', 'username', 'followers_count', 'following_count']

    def get_followers_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance
'''

# 동물인지 사람인지 따라 시리얼라이저 다르게 줘야됨.
class BaseProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    id=serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        fields = ['nickname', 'profile_pic', 'bio', 'username', 'followers_count', 'following_count', 'id']

    def get_followers_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()

class HumanProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = Profile

class AnimalProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = AnimalProfile
        fields = BaseProfileSerializer.Meta.fields + ['center', 'species', 'kind', 'sex', 'age', 'weight', 'enter', 'youtube', 'profile_pic_url']

class ProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'is_animal', 'profile', 'followers_count', 'following_count']

    def get_profile(self, obj):
        if obj.is_animal:
            try:
                serializer = AnimalProfileSerializer(obj.animalprofile)
            except AnimalProfile.DoesNotExist:
                return None
        else:
            try:
                serializer = HumanProfileSerializer(obj.profile)
            except Profile.DoesNotExist:
                return None
        return serializer.data

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()