from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    user_name = models.ForeignKey(User,related_name='page_writer',on_delete=models.CASCADE)
    content = models.TextField()
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user_name = models.ForeignKey(User,related_name='comment_writer',on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')


class FollowList(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE,null=True)
    following = models.ForeignKey(User, related_name='followers',on_delete=models.CASCADE,null=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"