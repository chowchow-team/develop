from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User,related_name='page_writer',on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    #title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.content[:30]
    
    def increment_view_count(self):
        self.view_count += 1
        self.save()

class Comment(models.Model):
    user = models.ForeignKey(User,related_name='comment_writer',on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')


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

class FollowList(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE,null=True)
    following = models.ForeignKey(User, related_name='followers',on_delete=models.CASCADE,null=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"