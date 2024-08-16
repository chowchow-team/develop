from datetime import datetime, timedelta, timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
import time


# 이미지 사이트 컨버트용
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.core.files.storage import default_storage
import os

import magic
import uuid
import re

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, is_animal=False):
        if not username:
            raise ValueError('must have username')
        user = self.model(
            username=username,
            # 사람일때만 이메일필드 사용하게할거야
            email=self.normalize_email(email) if not is_animal else None,
            is_animal=is_animal,
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password, email=None):
        email=username+'gmail.com'
        superuser = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        superuser.is_admin = True
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.is_active = True
        superuser.save()
        return superuser
    
class User(AbstractBaseUser):
    username_pattern = RegexValidator(r'^[0-9a-zA-Z_]{5,20}$', '5-20글자 사이의 숫자,영문,언더바만 가능합니다!')
    objects = UserManager()

    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    username = models.CharField(max_length=20, null=False,
                                unique=True, validators=[username_pattern])
    char_num = models.IntegerField(default=-1)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_animal = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'

    def set_password(self, raw_password):
        try:
            validate_password(raw_password, self)
        except ValidationError as e:
            raise ValidationError({"password": e.messages})
        super().set_password(raw_password)


    def get_required_fields(self):
        if self.is_animal:
            return []
        else:
            return ['email']

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            if self.is_animal:
                AnimalUser.objects.create(user=self)
                AnimalProfile.objects.create(user=self)
            else:
                Profile.objects.create(user=self)

    @classmethod
    def can_register(cls, username, email):
        if User.objects.filter(username=username, is_active=True).exists():
            return False, "이미 사용중인 사용자 이름입니다."
        if User.objects.filter(email=email, is_active=True).exists():
            return False, "이미 사용중인 이메일입니다."
        return True, ""

class AnimalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    animal_num = models.IntegerField(default=0)
    center = models.CharField(max_length=13, blank=True, default='익명의 챠우')
    species = models.CharField(max_length=100, blank=True)
    breed = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.species}"

class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=100)
    nickname = models.CharField(max_length=13, blank=True, default='익명의 챠우')

    class Meta:
        abstract = True

    def clean(self): #XSS 공격 방지(리액트에서 이스케이프처리되긴 하지만 서버에서 한번 더 처리했음)
        if self.bio and ('<' in self.bio or '>' in self.bio):
            raise ValidationError("자기소개란에는 HTML 태그를 사용할 수 없습니다.")
        if self.nickname and ('<' in self.nickname or '>' in self.nickname):
            raise ValidationError("닉네임에는 HTML 태그를 사용할 수 없습니다.")

    @transaction.atomic # 이미지 처리시간지연을 이용한 DoS 공격 방지함
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.pk:
            old_profile = self.__class__.objects.get(pk=self.pk)
            old_profile_pic = old_profile.profile_pic
            new_profile_pic = self.profile_pic
            if old_profile_pic.name != new_profile_pic.name:
                if old_profile_pic.name != self._meta.get_field('profile_pic').default:
                    old_profile_pic.delete(save=False)
                if new_profile_pic:
                    self.process_new_profile_pic()
        else:
            if self.profile_pic:
                self.process_new_profile_pic()
                
        super().save(*args, **kwargs)

    def process_new_profile_pic(self):
        # 파일 크기제한 10MB : 네이버블로그 정책 따라했음. 대용량파일 이용하는 DoS공격을 방지함.
        max_size = 10*1024*1024
        if self.profile_pic.size > max_size:
            raise ValueError("파일 크기는 10MB를 초과할 수 없습니다.")

        # 파일 확장자 검사 : 이중확장자 검사를 위해 모든 확장자를 추출해 검사했음
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
        file_name = self.profile_pic.name.lower()
        extensions = re.findall(r'\.([^.]+)', file_name)
        if not all(ext in allowed_extensions for ext in extensions):
            raise ValueError("허용되지 않는 파일 형식입니다.")


        # 매직 바이트 검사 : 파일의 매직 바이트를 이용해 파일 형식을 검사했음, 확장자만 바꿔 공격코드 업로드하는 경우 방지함.
        file_content = self.profile_pic.read()
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(file_content)
        allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']
        if file_mime not in allowed_mimes:
            raise ValueError("허용되지 않는 파일 형식입니다.")

        # 이미지 처리 : 이미지 리사이징으로 서버자원고갈 공격 방지함. 파일형식 고정해 안정성 확보.
        try: # 이미지 처리시간지연을 이용한 DoS 공격 방지함
            start_time=time.time()
            image = Image.open(BytesIO(file_content))
            image.verify()
            image = Image.open(BytesIO(file_content)) # 무결성검사하고 다시 안열면 에러남

            if time.time()-start_time>5: #5sec
                raise ValueError("이미지 처리시간이 너무 오래걸립니다.")
            output = BytesIO()
            image = image.resize((300, 300))
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(output, format='JPEG', quality=90)
            output.seek(0)
        except (IOError, SyntaxError, ValueError) as e:
            raise ValidationError(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")

        # 안전한 파일명 생성 : 혹시 예상치못한 파일명으로 가해질 수 있는 XSS 공격방지. 
        # UUID로 예측불가능한 파일명 생성함.
        safe_filename = f"{uuid.uuid4().hex}.jpg"
        
        self.profile_pic.save(
            safe_filename,
            content=InMemoryUploadedFile(output, 'ImageField', safe_filename, 'image/jpeg', sys.getsizeof(output), None),
            save=False
        )

        # 파일 실행 권한 제거 : 파일을 실행할 수 없게 권한 제거함.
        os.chmod(self.profile_pic.path, 0o644)


class Profile(BaseProfile):
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default.png')
    def __str__(self):
        return self.user.username

SPECIES_CHOICES = (
    ('0','고양이'),
    ('1','강아지'),
    ('2','ETC'),
)

class AnimalProfile(BaseProfile):
    center = models.CharField(max_length=13, blank=True, default='익명의 챠우')
    species = models.CharField(max_length=2, choices=SPECIES_CHOICES, default='0')
    kind = models.CharField(max_length=10, blank=True)
    sex = models.CharField(max_length=1, blank=True)
    age=models.CharField(max_length=12, blank=True) #max_length = 5
    weight = models.FloatField(null=True, blank=True)
    enter= models.DateTimeField(default=timezone.now)
    youtube=models.CharField(max_length=100, blank=True)
    profile_pic_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.species}"