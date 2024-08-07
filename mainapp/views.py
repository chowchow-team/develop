from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post,Comment,FollowList
from .serializers import PostSerializer,CommentSerializer,FollowListSerializer
from django.contrib.auth import get_user_model
from accountapp.serializers import AccountCreateSerializer
from .services import FollowService

User = get_user_model()
class PostRecentAPIView(APIView): # 가장 최근에 포스트된 게시물 5개를 받아오는 역할 -> 잘 동작함
    def get(self,request):
        posts = Post.objects.all().order_by('-timestamp')[:5]
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)

class PostFollowAPIView(APIView): # 팔로우하는 객체의 포스팅 5개를 받아오는 역할
    def get(self,request):
        id = request.GET.get('id','')
        if id:
            follow_objects = FollowList.objects.filter(id=id).order_by('?')[:5]
            follow_names = [follow.following for follow in follow_objects]
            recent_posts = []
            for follow_name in follow_names:
                recent_post = Post.objects.filter(follow_name = follow_name).order_by('-timestmap').first()
                if recent_post:
                    recent_posts.append(recent_post)
            serializer = PostSerializer(recent_posts,many=True)
            return Response(serializer.data)
        return Response()

            
class PostControlAPIView(APIView): # 페이지 생성, 불러오기
    def post(self,request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_name=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self,request):
        title = request.GET.get('title','')
        timestamp = request.GET.get('timestamp','')
        filters = {}
        if title:
            filters['title'] = title
        if timestamp:
            filters['timestamp'] = timestamp
        
        post = Post.objects.filter(**filters)
        serializer = PostSerializer(post)
        return Response(serializer.data)

class CommentControlAPIView(APIView): # Post에 작성된 comment를 get하거나 comment를 생성하는 것
    def post(self,request,post_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_name=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request,id):
        post = Post.objects.filter(id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class FollowRecommandAPIView(APIView): # 동작함 -> 본인이 추천되는 것만 빼자
    def get(self,request):
        users = User.objects.all().order_by('?')[:5]
        serializer = AccountCreateSerializer(users,many=True)
        return Response(serializer.data)

class FollowerListAPIView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        followers = FollowService.get_followers(user)
        serializer = AccountCreateSerializer(followers, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

class FollowingListAPIView(APIView):
    def get(self,request):
        user_id = request.GET.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        followings = FollowService.get_following(user)
        serialzier = AccountCreateSerializer(followings,many=True)
        return Response({"status": "success", "data": serializer.data}, status=200)

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

class UnfollowRequestAPIView(APIView):
    def post(self, request):
        following_id = request.data.get('following_id')
        follower_id = request.data.get('follower_id')

        try:
            follower = User.objects.get(id=follower_id)
            following = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        FollowService.unfollow(follower, following)
        
        return Response({"status": "success"}, status=status.HTTP_200_OK)


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