from rest_framework import serializers
from .models import Post, Comment, PostImage
from accountapp.models import User

class UserSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'school', 'school_name']

    def get_school_name(self, obj):
        return obj.get_school_display()
    
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image']

class PostSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    def get_type_display(self, obj):
        return obj.get_type_display()

    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'created_at', 
                  'updated_at', 'view_count', 'type', 'type_display', 
                  'comments_count', 'images']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        images_data = self.context.get('images', [])
        post = Post.objects.create(**validated_data)
        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)
        return post

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'post']
