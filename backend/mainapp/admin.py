from django.contrib import admin
from .models import Post, Comment,FollowList, PostImage, Like
# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(FollowList)
admin.site.register(Like)

admin.site.register(PostImage)