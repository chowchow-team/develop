from datetime import datetime, timedelta, timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
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

    def create_user(self, username, email=None, password=None):
        if not username:
            raise ValueError('must have username')
        user=self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password):
        superuser=self.create_user(
            username=username,
            email=email,
            password=password,
        )
        superuser.is_admin=True
        superuser.is_superuser=True
        superuser.is_staff=True
        superuser.is_active=True
        superuser.save()
        return superuser
    
class User(AbstractBaseUser):
    username_pattern = RegexValidator(r'^[0-9a-zA-Z_]{5,20}$', '5-20글자 사이의 숫자,영문,언더바만 가능합니다!')
    objects = UserManager()

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=20, null=False,
                                unique=True, validators=[username_pattern])
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            Profile.objects.create(user=self)

    @classmethod
    def can_register(cls, username, email):
        if User.objects.filter(username=username, is_active=True).exists():
            return False, "이미 사용중인 사용자 이름입니다."
        if User.objects.filter(email=email, is_active=True).exists():
            return False, "이미 사용중인 이메일입니다."
        return True, ""
    

User = get_user_model()
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=13, blank=True, default='익명의 챠우')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default.png')
    bio = models.TextField(blank=True, max_length=100)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_profile = Profile.objects.get(pk=self.pk)
            old_profile_pic = old_profile.profile_pic
            new_profile_pic = self.profile_pic
            if old_profile_pic.name != new_profile_pic.name:
                if old_profile_pic.name != 'profile_pics/default.png':
                    old_profile_pic.delete(save=False)
                if new_profile_pic:
                    self.process_new_profile_pic()
        else:
            if self.profile_pic:
                self.process_new_profile_pic()
                
        super(Profile, self).save(*args, **kwargs)

    def process_new_profile_pic(self):
        image = Image.open(self.profile_pic)
        output = BytesIO()
        image = image.resize((300, 300))
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(output, format='JPEG', quality=90)
        output.seek(0)
        self.profile_pic.save(self.profile_pic.name, content=InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % os.path.splitext(self.profile_pic.name)[0], 'image/jpeg', sys.getsizeof(output), None), save=False)
