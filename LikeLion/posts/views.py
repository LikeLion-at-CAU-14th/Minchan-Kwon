### DRF 관련 import - APIView 사용
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly # jwt 세션
from .permissions import TimeRestrictedPermission, IsAuthorReadOnly

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

class PostList(APIView):
    permission_classes = [TimeRestrictedPermission]
    # 새로운 게시글 작성 (POST 요청)
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 게시글 전체 목록 가져오기 (GET 요청)
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
    permission_classes = [TimeRestrictedPermission, IsAuthenticatedOrReadOnly, IsAuthorReadOnly]
    # 특정 게시글 상세 정보 가져오기 (GET 요청)
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    # 특정 게시물 정보 수정하기 (PUT 요청)
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        self.check_object_permissions(request, post)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 특정 게시물 삭제하기 (DELETE 요청)
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        self.check_object_permissions(request, post)

        post.delete()
        return Response(
            {
                "message": "게시글이 성공적으로 삭제되었습니다.",
	            "post_id": post_id
            },
            status=status.HTTP_200_OK
        )
    
class CommentList(APIView):
    permission_classes = [TimeRestrictedPermission]
    # 특정 게시글의 모든 댓글 가져오기 (GET 요청)
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {
            'status': status.HTTP_200_OK,
            'message': '특정 게시물 목록 모든 comment 조회 성공',
            'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    # 특정 게시글에 댓글 작성
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetail(APIView):
    permission_classes = [TimeRestrictedPermission]
    # 특정 게시글에 댓글 삭제
    def delete(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)
        comment.delete()
        return Response(
            {
                "message": "댓글이 성공적으로 삭제되었습니다.",
	            "comment_id": comment_id
            },
            status=status.HTTP_200_OK
        )