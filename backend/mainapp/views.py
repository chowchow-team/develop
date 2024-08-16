from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post,Comment,FollowList,PostImage,Like
from .serializers import PostSerializer,CommentSerializer,FollowListSerializer, FollowingListSerializer
from django.contrib.auth import get_user_model
from accountapp.serializers import AccountCreateSerializer
from .services import FollowService
import random
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import FileResponse
import os
import mimetypes
from urllib.parse import quote
from django.conf import settings

User = get_user_model()
class PostRecentAPIView(APIView):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        posts = Post.objects.all().order_by('-timestamp')[offset:offset+limit+1]
        has_next = len(posts) > limit
        posts = posts[:limit]
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response({
            "results": serializer.data,
            "next": has_next
        })

class PostFollowAPIView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"status": "error", "message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))

        following_ids = FollowService.get_following(user)
        
        posts = Post.objects.filter(user_id__in=following_ids).order_by('-timestamp')[offset:offset+limit+1]
        
        has_next = len(posts) > limit
        posts = posts[:limit]
        
        serializer = PostSerializer(posts, many=True, context={'request': request})
        
        return Response({
            "results": serializer.data,
            "next": has_next
        })

# 현장미션0816
class PostControlAPIView(APIView):
    def post(self, request):
        images = request.FILES.getlist('images', [])
        file = request.FILES.get('file')

        if file and file.size > 200 * 1024 * 1024:  # 200MB
            return Response({"error": "파일 크기는 200MB를 초과할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if len(images) > 4:
            return Response({"error": "최대 4개의 이미지만 업로드할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(data=request.data, context={'images': images, 'file': file, 'request': request})
        
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "게시물을 생성하는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        post_id = request.GET.get('post_id')
        download = request.GET.get('download', 'false').lower() == 'true'

        if not post_id:
            return Response({"status": "error", "message": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = get_object_or_404(Post, id=post_id)

            if download:
                return self.download_file(request, post)

            viewed_posts = request.COOKIES.get('viewed_posts', '')
            viewed_posts_list = viewed_posts.split(',') if viewed_posts else []

            if str(post_id) not in viewed_posts_list:
                post.increment_view_count()
                viewed_posts_list.append(str(post_id))
                new_viewed_posts = ','.join(viewed_posts_list)
                
                serializer = PostSerializer(post, context={'request': request})
                response = Response(serializer.data)
                response.set_cookie('viewed_posts', new_viewed_posts, max_age=60*24*60*60, httponly=True, samesite='Lax')
                return response
            else:
                serializer = PostSerializer(post, context={'request': request})
                return Response(serializer.data)

        except Post.DoesNotExist:
            return Response({"status": "error", "message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def download_file(self, request, post):
        if not post.file:
            return Response({"error": "이 게시물에는 파일이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        file_path = post.file.path
        
        try:
            file_path = os.path.abspath(file_path)
            base_dir = os.path.abspath(settings.MEDIA_ROOT)
            if not file_path.startswith(base_dir):
                return Response({"error": "잘못된 파일 경로입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "잘못된 파일 경로입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(file_path):
            return Response({"error": "파일을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        content_type, encoding = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        
        if file_name.endswith('.hwp'):
            content_type = 'application/x-hwp'
        elif file_name.endswith('.xlsx'):
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_name.endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        try:
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{quote(file_name)}"; filename*=UTF-8\'\'{quote(file_name)}'
            response['Content-Length'] = file_size
            return response
        except Exception as e:
            return Response({"error": "파일을 열 수 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommentControlAPIView(APIView):
    def post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({"error": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        post_id = request.GET.get('post_id')
        if not post_id:
            return Response({"error": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comments = Comment.objects.filter(post=post).order_by('-timestamp')[offset:offset+limit+1]
        
        has_next = len(comments) > limit
        comments = comments[:limit]
        
        serializer = CommentSerializer(comments, many=True)
        
        return Response({
            "results": serializer.data,
            "next": has_next
        })


class FollowRecommandAPIView(APIView): # 동작함 -> 본인이 추천되는 것만 빼자
    def get(self,request):
        user_id = 3 #request.GET.get('user_id') -> 프론트엔드에서 전송함
        users = User.objects.exclude(id=user_id).order_by('?')[:5]
        serializer = AccountCreateSerializer(users,many=True)
        return Response(serializer.data)

class FollowerListAPIView(APIView): # 아이디, 유저네임 둘다 가능하게바꿨음.
    def get(self, request):
        user_id = request.GET.get('user_id')
        username = request.GET.get('username')

        if not user_id and not username:
            return Response({"status": "error", "message": "Either user_id or username is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        follower_ids = FollowService.get_follower(user)
        followers = User.objects.filter(id__in=follower_ids).select_related('profile', 'animalprofile')
        serializer = FollowingListSerializer(followers, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


class FollowingListAPIView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        username = request.GET.get('username')

        if not user_id and not username:
            return Response({"status": "error", "message": "Either user_id or username is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        following_ids = FollowService.get_following(user)
        followings = User.objects.filter(id__in=following_ids).select_related('profile', 'animalprofile')
        serializer = FollowingListSerializer(followings, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


class FollowRequestAPIView(APIView):
    def post(self, request):
        following_id = request.data.get('following_id')
        follower_id = request.data.get('follower_id')

        if not following_id or not follower_id:
            return Response({"status": "error", "message": "Both follower and following identifiers are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follower = self.get_user(follower_id)
            following = self.get_user(following_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        FollowService.follow(follower, following)
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    def get_user(self, identifier):
        """
        Get user by id or username
        """
        if isinstance(identifier, int) or identifier.isdigit():
            return User.objects.get(id=int(identifier))
        else:
            return User.objects.get(username=identifier)


class UnfollowRequestAPIView(APIView):
    def post(self, request):
        following_id = request.data.get('following_id')
        follower_id = request.data.get('follower_id')

        if not following_id or not follower_id:
            return Response({
                "message": "Both follower_id and following_id are required",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            follower = self.get_user(follower_id)
            following = self.get_user(following_id)
        except User.DoesNotExist:
            return Response({
                "message": "User not found",
                "status": "error"
            }, status=status.HTTP_404_NOT_FOUND)

        FollowService.unfollow(follower, following)
        
        return Response({
            "message": "Successfully unfollowed",
            "status": "success"
        }, status=status.HTTP_200_OK)

    def get_user(self, identifier):
        """
        Get user by id or username
        """
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            return User.objects.get(id=int(identifier))
        else:
            return User.objects.get(username=identifier)


class FollowCheckAPIView(APIView): #frontend에서 follow <-> unfollow 버튼 전환을 위해 사용
    def get(self, request):

        follower_id = request.GET.get('follower_id')
        following_id = request.GET.get('user_id')

        if not follower_id or not following_id:
            return Response({"error": "Missing follower_id or user_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follower = User.objects.get(id=follower_id)
        except User.DoesNotExist:
            return Response({"error": "Follower user does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            following = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({"error": "Following user does not exist"}, status=status.HTTP_404_NOT_FOUND)

        is_following = FollowService.is_following(follower, following)
        return Response({"isFollowing": is_following}, status=status.HTTP_200_OK)

class UserPostListView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=user).order_by('-timestamp')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        start = (page - 1) * limit
        end = start + limit

        posts_page = posts[start:end + 1]
        has_next = len(posts_page) > limit
        posts_page = posts_page[:limit]

        serializer = PostSerializer(posts_page, many=True, context={'request': request})
        
        return Response({
            "results": serializer.data,
            "has_next": has_next
        }, status=status.HTTP_200_OK)
    


class LikePostAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        post_id = request.data.get('post_id')
        user = request.user

        post = get_object_or_404(Post, id=post_id)
        
        like, created = Like.objects.get_or_create(user=user, post=post)
        
        if not created:
            # 이미 좋아요를 눌렀다면 좋아요 취소
            like.delete()
            post.likes.remove(user)
            status_msg = "unliked"
        else:
            post.likes.add(user)
            status_msg = "liked"
        
        like_count = post.like_count()
        return Response({"status": status_msg, "like_count": like_count}, status=status.HTTP_200_OK)
    
class UserLikedPostsAPIView(APIView):
    def get(self, request):
        user = request.user
        liked_posts = Post.objects.filter(likes=user)
        serializer = PostSerializer(liked_posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
