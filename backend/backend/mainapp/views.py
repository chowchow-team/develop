from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post,Comment,FollowList
from .serializers import PostSerializer,CommentSerializer,FollowListSerializer
from django.contrib.auth import get_user_model
from accountapp.serializers import AccountCreateSerializer
User = get_user_model()
class PostRecentAPIView(APIView): # 가장 최근에 포스트된 게시물 5개를 받아오는 역할
    def get(self,request):
        posts = Post.objects.all().order_by('-timestamp')[:5]
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)

class PostFollowAPIView(APIView): # 팔로우하는 객체의 포스팅 5개를 받아오는 역할
    def get(self,request):
        id = request.GET.get('id','')
        if id:
            follow_objects = FollowList.objects.filter(id=id).order_by('?')[:5]
            follow_names = [follow.name_follow for follow in follow_objects]
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
            serializer.save(writer=request.user)
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

class CommentControlAPIView(APIView):
    def post(self,request,post_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        id = request.GET.get('id','')
        post = Post.objects.filter(id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class FollowRecommandAPIView(APIView): # 동작함 -> 본인이 추천되는 것만 빼자
    def get(self,request):
        users = User.objects.all().order_by('?')[:5]
        serializer = AccountCreateSerializer(users,many=True)
        return Response(serializer.data)

class FollowListAPIView(APIView):
    def get(self,request):
        user_name = request.GET.get('name_follow')
        users = User.objects.all().filter(name_follow=user_name)
        serializer = AccountCreateSerializer(users,many=True)
        return Response({"status":"success"},serializer.data)
    

class FollowRequestAPIView(APIView): # 동작함
    def post(self, request):
        name_follow = request.data.get('name_follow')
        name_follower = request.data.get('name_follower')

        if not name_follow or not name_follower:
            return Response({"error": "Missing name_follow or name_follower"}, status=status.HTTP_400_BAD_REQUEST)
        
        follow_users = User.objects.filter(username=name_follow)
        
        if not follow_users.exists():
            return Response({"error": "User to follow does not exist"}, status=status.HTTP_404_NOT_FOUND)

        follow_instance = FollowList.objects.create(name_follow=name_follow, name_follower=name_follower)
        follow_instance.follow.set(follow_users)
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)