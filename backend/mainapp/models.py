from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
import sys
import os
import time
import uuid
import magic
import re
from django.db import transaction

User = get_user_model()

def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    sanitized_name = get_valid_filename(name)
    sanitized_name = sanitized_name[:100]  # 파일명 길이 제한
    return f"{sanitized_name}{ext}"

def get_file_path(instance, filename):
    sanitized_filename = sanitize_filename(filename)
    ext = os.path.splitext(sanitized_filename)[1].lower()
    uuid_part = uuid.uuid4().hex[:8]
    new_filename = f"{uuid_part}_{sanitized_filename}"
    return os.path.join('post_files', new_filename)

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.hwp', '.xlsx', '.xls', '.docx', '.doc']
    if ext not in valid_extensions:
        raise ValidationError('지원되지 않는 파일 형식입니다.')

def validate_file_size(value):
    filesize = value.size
    if filesize > 200 * 1024 * 1024:  # 200MB
        raise ValidationError("최대 파일 크기는 200MB입니다.")

def validate_file_type(value):
    allowed_types = {
        'application/pdf': '.pdf',
        'application/x-hwp': '.hwp',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/msword': '.doc',
        'application/x-ole-storage': ['.doc', '.xls']
    }
    
    file_content = value.read(1024)
    value.seek(0)
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file_content)
    
    if file_mime not in allowed_types:
        print("file_mime: ",file_mime)
        raise ValidationError("파일 내용이 허용되지 않는 형식입니다:", file_mime)

class Post(models.Model):
    user = models.ForeignKey(User, related_name='page_writer', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    file = models.FileField(
        upload_to=get_file_path,
        validators=[validate_file_extension, validate_file_size, validate_file_type],
        null=True,
        blank=True
    )

    def __str__(self):
        return self.content[:30]
    
    def increment_view_count(self):
        self.view_count += 1
        self.save()
    
    def like_count(self):
        return self.likes.count()
    
    @transaction.atomic
    def save_with_file(self, file):
        try:
            self.full_clean()
            if file:
                sanitized_filename = sanitize_filename(file.name)
                file.name = sanitized_filename
                self.file = file
            super().save()
        except ValidationError as e:
            raise ValidationError(f"게시물 저장 실패: {str(e)}")
        except Exception as e:
            raise Exception(f"게시물 저장 중 오류 발생: {str(e)}")
    
    @transaction.atomic
    def save_with_images(self, image_files):
        try:
            self.full_clean()
            super().save()
            
            for image_file in image_files:
                sanitized_filename = sanitize_filename(image_file.name)
                image_file.name = sanitized_filename
                post_image = PostImage(post=self, image=image_file)
                post_image.full_clean()
                post_image.save()

        except ValidationError as e:
            raise ValidationError(f"게시물 저장 실패: {str(e)}")
        except Exception as e:
            raise Exception(f"게시물 저장 중 오류 발생: {str(e)}")

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comment_writer', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

class PostImage(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')

    def clean(self):
        if self.image:
            self.validate_image()

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.pk:
            old_instance = PostImage.objects.get(pk=self.pk)
            if old_instance.image != self.image:
                if old_instance.image:
                    old_instance.image.delete(save=False)
                if self.image:
                    self.process_new_image()
        else:
            if self.image:
                self.process_new_image()
        
        super().save(*args, **kwargs)

    def validate_image(self):
        max_size = 10 * 1024 * 1024  # 10MB
        if self.image.size > max_size:
            raise ValidationError("파일 크기는 10MB를 초과할 수 없습니다.")

        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
        file_name = self.image.name.lower()
        extensions = re.findall(r'\.([^.]+)', file_name)
        if not extensions:
            raise ValidationError("파일에 확장자가 없습니다.")
        if not all(ext in allowed_extensions for ext in extensions):
            raise ValidationError(f"허용되지 않는 파일 형식입니다. 허용된 확장자: {', '.join(allowed_extensions)}")

        try:
            file_content = self.image.read()
            mime = magic.Magic(mime=True)
            file_mime = mime.from_buffer(file_content)
            allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']
            if file_mime not in allowed_mimes:
                raise ValidationError(f"허용되는 파일 형식은 JPEG, PNG, GIF입니다. 감지된 형식: {file_mime}")
            Image.open(BytesIO(file_content)).verify()
        except Exception as e:
            raise ValidationError(f"유효하지 않은 이미지 파일입니다: {str(e)}")
        finally:
            self.image.seek(0)

    def process_new_image(self):
        try:
            start_time = time.time()
            with Image.open(self.image) as image:
                if time.time() - start_time > 5:  # 5초
                    raise ValidationError("이미지 처리시간이 너무 오래걸립니다.")

                output = BytesIO()
                image = image.resize((1080, 1080))
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(output, format='JPEG', quality=90)
                output.seek(0)

            safe_filename = f"{uuid.uuid4().hex}.jpg"
            
            self.image.save(
                safe_filename,
                content=InMemoryUploadedFile(output, 'ImageField', safe_filename, 'image/jpeg', sys.getsizeof(output), None),
                save=False
            )

            os.chmod(self.image.path, 0o644)
        except Exception as e:
            raise ValidationError(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")        

class FollowList(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE, null=True)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"