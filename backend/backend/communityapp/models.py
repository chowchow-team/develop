from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image


User = get_user_model()

TYPE_CHOICES = (('0', '랜덤채팅'),
            ('1', '썸/연애'),
            ('2', '주식/투자'),
            ('3', '재수/반수/편입'),
            ('4', '취업/창업'),
            ('5', '여행/먹방'),
            ('6', '게임'),
            ('7', '패션/뷰티'),
            ('8', '유머'),
            ('9', '군대'),
            ('10', '팀원모집/프로젝트'))

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='0')
    
    # Meta 클래스를 사용해 게시물의 기본 정렬 순서를 최신 순으로 설정
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.view_count += 1
        self.save()

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        
        if img.height > 1080 or img.width > 1080:
            output_size = (1080, 1080)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # 한 사용자가 같은 게시물에 여러 번 좋아요를 누르지 못하도록 설정

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
