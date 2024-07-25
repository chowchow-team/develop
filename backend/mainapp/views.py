from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post,Comment,FollowList
from .serializers import PostSerializer,CommentSerializer,FollowListSerializer
from accountapp.models import UserManager
from accountapp.serializers import AccountCreateSerializer
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
        writer = request.data.get('writer')
        content = request.data.get('content')
        title = request.data.get('title')
        timestamp = request.data.get('timestamp')
        post = Post.objects.create(writer=writer,content=content,title=title,timestamp=timestamp)
        serializer = PostSerializedr(post)
        return Response(serializer.data)
    def get(self,request):
        title = request.GET.get('title','')
        timestamp = request.GET.get('timestamp','')
        post = Post.objects.filter(title=tile,timestamp=timestamp)
        serializer = PostSerializer(post)
        return Response(serializer.data)

class CommentControlAPIView(APIView):
    def post(self,request):
        writer = request.data.get('writer')
        content = request.data.get('content')
        timestamp = request.data.get('timestamp')
        comment = Comment.objects.create(writer=writer,content=content,timestamp=timestamp)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    def get(self,request):
        id = request.GET.get('id','')
        post = Post.objects.filter(id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class FollowRecommandAPIView(APIView):
    def get(self,request):
        users = UserManager.all().order_by('?')[:5]
        serializer = AccountCreateSerializer(users,many=True)
        return Response(serializer.data)