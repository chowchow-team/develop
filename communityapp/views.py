from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class PostCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data, context={'request': request, 'images': request.FILES.getlist('images')})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostDeleteAPI(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.posts.all()  # 사용자가 작성한 글만 삭제할 수 있도록 설정

class PostListAPI(ListAPIView):
    serializer_class = PostSerializer
    def get_queryset(self):
        queryset = Post.objects.all()
        # URL에서 type 파라미터를 가져오기
        post_type = self.request.query_params.get('type', None)
        if post_type is not None:
            queryset = queryset.filter(type=post_type)
        return queryset

class PostDetailView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        # 쿠키에서 읽은 게시물의 ID 목록을 가져옴
        viewed_posts = request.COOKIES.get('viewed_posts', '')

        if str(pk) not in viewed_posts:
            # 현재 게시물의 ID가 목록에 없으면 조회수를 증가시키고 쿠키를 업데이트함
            post.increment_view_count()
            # 쿠키에 현재 게시물의 ID 추가
            new_viewed_posts = f'{viewed_posts},{pk}' if viewed_posts else str(pk)
            response = Response(PostSerializer(post).data)
            # 쿠키 설정 (예: 30일 동안 유효)
            response.set_cookie('viewed_posts', new_viewed_posts, max_age=30*24*60*60)
            return response
        else:
            # 쿠키에 이미 게시물 ID가 있으면, 조회수를 증가시키지 않고 응답만 반환
            return Response(PostSerializer(post).data)

class LikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'message': '좋아요!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': '이미 좋아요를 눌렀습니다.'}, status=status.HTTP_409_CONFLICT)

class UnlikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        like = Like.objects.filter(user=request.user, post_id=post_id)
        
        if like.exists():
            like.delete()
            return Response({'message': '좋아요 취소됨.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '좋아요를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


class CommentCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#class CommentListAPI(APIView):
#    def get(self, request, post_id):
#        comments = Comment.objects.filter(post_id=post_id)
#        serializer = CommentSerializer(comments, many=True)
#        return Response(serializer.data)
    

class CommentListAPI(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)