from rest_framework import serializers
from django.core.exceptions import ValidationError
from utils.school_loader import load_schools_from_json
from .models import User, Profile
import json

from PIL import Image
from django.core.files.base import ContentFile
import io
import os
from django.conf import settings

class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        school_domains = load_schools_from_json()

        domain = value.split('@')[1]
        school = self.initial_data['school']

        try:
            school_id = int(school)
        except ValueError:
            raise ValidationError("학교 ID가 유효하지 않습니다.")

        # 학교 ID를 기반으로 도메인 정보 찾기
        school_domain_info = next((item for item in school_domains if item['id'] == school_id), None)
        # 학교 정보가 없거나 도메인 영역이 빈 배열일 경우 예외 처리
        if school_domain_info is None or not school_domain_info['domains']:
            raise ValidationError("해당 학교는 아직 준비중입니다.")

        # 도메인 검증
        if domain not in school_domain_info['domains']:
            raise ValidationError("자신의 학교 계정 이메일을 입력해주세요!")

        return value

    def create(self, validated_data):
        # 사용자 생성 로직
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

#class ProfileSerializer(serializers.ModelSerializer):
#    username = serializers.CharField(source='user.username')
#
#    class Meta:
#        model = Profile
#        fields = ['nickname', 'profile_pic', 'bio', 'username']
#
#    def update(self, instance, validated_data):
#        instance.nickname = validated_data.get('nickname', instance.nickname)
#        instance.bio = validated_data.get('bio', instance.bio)
#        
#        if 'profile_pic' in validated_data:
#            profile_pic = validated_data.pop('profile_pic')
#            if profile_pic.name.endswith(('.heif', '.HEIF', '.heic', '.HEIC')):
#                heif_file = pyheif.read(profile_pic)
#                image = Image.frombytes(
#                    heif_file.mode, 
#                    heif_file.size, 
#                    heif_file.data,
#                    "raw",
#                    heif_file.mode,
#                    heif_file.stride,
#                )
#            else:
#                image = Image.open(profile_pic)
#
#            # 이제 모든 이미지를 PNG로 저장하는 save_image_as_png 함수를 사용
#            save_image_as_png(image, instance)
#
#        instance.save()
#        return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ['nickname', 'profile_pic', 'bio', 'username']

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance