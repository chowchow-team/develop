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

User = get_user_model()

'''
class PostRecentAPIView(APIView): # 가장 최근에 포스트된 게시물 5개를 받아오는 역할 -> 잘 동작함
    def get(self,request):
        page = int(request.GET.get('page'))
        #if page in self.uploaded_pages:
        #    return Response([])
        all_posts = Post.objects.all().order_by('-timestamp')
        total_posts = all_posts.count()
        start_index = (page-1)*5
        end_index = start_index + 5
        if start_index >= total_posts:
            return Response([])
        posts = all_posts[start_index:end_index]
        serializer = PostSerializer(posts,many=True)
        self.uploaded_pages.add(page)
        return Response(serializer.data)
'''
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

'''
class PostFollowAPIView(APIView): # 팔로우하는 객체의 포스팅 5개를 받아오는 역할 -> 잘 동작함
    def get(self,request):
        user_id = 3 #request.GET.get('user_id') -> 'user_id'는 frontend에서 전달
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        following_ids = FollowService.get_following(user)
        followings = User.objects.filter(id__in=following_ids)
        if not followings:
            return Response([])
        selected_followings = random.sample(list(followings),min(len(followings),5))
        posts = []
        for following in selected_followings:
            post = Post.objects.filter(user=following).order_by('-timestamp').first()
            if post:
                posts.append(post)
        serializer = PostSerializer(posts,many=True)
        return Response({"status": "success", "posts": serializer.data}, status=status.HTTP_200_OK)
'''

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

'''
class PostControlAPIView(APIView):
    def post(self, request):
        images = request.FILES.getlist('images')
        serializer = PostSerializer(data=request.data, context={'images': images, 'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        post_id = request.GET.get('post_id')
        if not post_id:
            return Response({"status": "error", "message": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
            viewed_posts = request.COOKIES.get('viewed_posts', '')

            if viewed_posts:
                viewed_posts_list = viewed_posts.split(',')
            else:
                viewed_posts_list = []

            if str(post_id) not in viewed_posts_list:
                post.increment_view_count()
                viewed_posts_list.append(str(post_id))
                new_viewed_posts = ','.join(viewed_posts_list)
                
                response = Response(PostSerializer(post).data)
                response.set_cookie('viewed_posts', new_viewed_posts, max_age=60*24*60*60)
                return response
            else:
                return Response(PostSerializer(post).data)
        except Post.DoesNotExist:
            return Response({"status": "error", "message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
 '''
class PostControlAPIView(APIView):
    def get(self, request):
        post_id = request.GET.get('post_id')
        if not post_id:
            return Response({"status": "error", "message": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
            viewed_posts = request.COOKIES.get('viewed_posts', '')

            if viewed_posts:
                viewed_posts_list = viewed_posts.split(',')
            else:
                viewed_posts_list = []

            if str(post_id) not in viewed_posts_list:
                post.increment_view_count()
                viewed_posts_list.append(str(post_id))
                new_viewed_posts = ','.join(viewed_posts_list)
                
                serializer = PostSerializer(post, context={'request': request})
                response = Response(serializer.data)
                response.set_cookie('viewed_posts', new_viewed_posts, max_age=60*24*60*60)
                return response
            else:
                serializer = PostSerializer(post, context={'request': request})
                return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"status": "error", "message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

   
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

'''
class FollowerListAPIView(APIView): # 유저를 팔로우 하는 객체 리스트
    def get(self, request):
        user_id = request.GET.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        follower_ids = FollowService.get_follower(user)
        followers = User.objects.filter(id__in=follower_ids).select_related('profile', 'animalprofile')
        serializer = FollowingListSerializer(followers, many=True)
        return Response({"status": "success", "data": serializer.data}, status=200)
'''
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

"""
class FollowRequestAPIView(APIView):
    def post(self, request):
        following_id = request.data.get('following_id')
        follower_id = request.data.get('follower_id')

        try:
            follower = User.objects.get(id=follower_id)
            following = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        FollowService.follow(follower, following)
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)
"""
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
