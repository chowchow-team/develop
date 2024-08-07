from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    writer = models.ForeignKey(User,related_name='page_writer',on_delete=models.CASCADE)
    content = models.TextField()
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    writer = models.ForeignKey(User,related_name='comment_writer',on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')


class FollowList(models.Model):
    name_follow = models.CharField(max_length=100)
    name_follower = models.CharField(max_length=100)
    follow = models.ManyToManyField(User)
