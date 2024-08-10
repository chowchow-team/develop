from datetime import datetime, timedelta, timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone

# 이미지 사이트 컨버트용
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.core.files.storage import default_storage
import os

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
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_animal = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
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

    def save(self, *args, **kwargs):
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
        image = Image.open(self.profile_pic)
        output = BytesIO()
        image = image.resize((300, 300))
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(output, format='JPEG', quality=90)
        output.seek(0)
        self.profile_pic.save(self.profile_pic.name, content=InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % os.path.splitext(self.profile_pic.name)[0], 'image/jpeg', sys.getsizeof(output), None), save=False)

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
    '''
    센터명: 마포센터 // 이름에서 추출. 설탕(마포센터-임시보호가능): '(' 뒤부터이름, '-'또는 ')' 앞까지 센터명 
    종
    품종
    성별: W:암컷, M:수컷
    나이: 0/2 형식으로 저장. 0세2개월
    체중: 0.0 형식으로 저장
    입소일: 2021-01-01 형식으로 저장. "2011-09-01T13:20:30+03:00" 형식변환 체크
    소개영상: 유튜브 링크
    프로필사진: 이미지파일(유투브 링크 썸네일 추출)
    '''
    center = models.CharField(max_length=13, blank=True, default='익명의 챠우')
    species = models.CharField(max_length=2, choices=SPECIES_CHOICES, default='0')
    kind = models.CharField(max_length=10, blank=True)
    sex = models.CharField(max_length=1, blank=True)
    age=models.CharField(max_length=5, blank=True)
    weight = models.FloatField(null=True, blank=True)
    enter= models.DateTimeField(default=timezone.now)
    youtube=models.CharField(max_length=100, blank=True)
    profile_pic_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.species}"