import os
import uuid
import boto3

from config.custom_exceptions import PostNotFoundException

from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.core.files.storage import default_storage  
from django.conf import settings
from django.views.decorators.http import require_http_methods

# DRF 관련 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly # jwt 세션
from rest_framework.parsers import MultiPartParser, FormParser  # 이미지 업로드용 파서

from .permissions import TimeRestrictedPermission, IsAuthorReadOnly, IsAvailableTime, IsOwnerOrReadOnly
from .models import Post, Comment, Image
from .serializers import PostSerializer, CommentSerializer, ImageSerializer

# Swagger 관련 import
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PostList(APIView):
    permission_classes = [TimeRestrictedPermission]

    @swagger_auto_schema(
        operation_summary="게시글 생성",
        operation_description="새로운 게시글을 생성합니다.",
        request_body=PostSerializer,
        responses={201: PostSerializer, 400: "잘못된 요청"},
    )

    # 새로운 게시글 작성 (POST 요청)
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글 목록을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    # 게시글 전체 목록 가져오기 (GET 요청)
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
    permission_classes = [TimeRestrictedPermission, IsAuthenticatedOrReadOnly, IsAuthorReadOnly]

    @swagger_auto_schema(
        operation_summary="게시글 상세 조회",
        operation_description="특정 ID를 가진 게시글의 상세 정보를 조회합니다.",
        responses={200: PostSerializer, 404: "게시글을 찾을 수 없음"}
    )
    # 특정 게시글 상세 정보 가져오기 (GET 요청)
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="게시글 수정",
        operation_description="특정 ID를 가진 게시글의 내용을 수정합니다.",
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "잘못된 요청", 403: "권한 없음", 404: "게시글을 찾을 수 없음"}
    )
    # 특정 게시물 정보 수정하기 (PUT 요청)
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        self.check_object_permissions(request, post)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 삭제",
        operation_description="특정 ID를 가진 게시글을 성공적으로 삭제합니다.",
        responses={200: "삭제 성공 알림", 403: "권한 없음", 404: "게시글을 찾을 수 없음"}
    )
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

    @swagger_auto_schema(
        operation_summary="특정 게시글의 댓글 목록 조회",
        operation_description="게시글 ID에 속한 모든 댓글 조회를 요청합니다.",
        responses={200: "댓글 목록 반환 완료"}
    )
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
    
    @swagger_auto_schema(
        operation_summary="특정 게시글에 댓글 작성",
        operation_description="게시글 ID를 지정하여 새로운 댓글을 작성합니다.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "잘못된 요청"}
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

    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        operation_description="특정 게시글에 속한 특정 댓글을 성공적으로 삭제합니다.",
        responses={200: "댓글 삭제 성공 알림", 404: "댓글 또는 게시글을 찾을 수 없음"}
    )
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
    
class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="S3 이미지 업로드 (중복 방지)",
        operation_description="실제 이미지 파일을 form-data 형태로 받아 S3 버킷에 고유한 이름으로 업로드하고 주소를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                name="image",          # request.FILES['image'] 키값과 매칭
                in_=openapi.IN_FORM,   # form-data 설정
                type=openapi.TYPE_FILE,
                required=True,
                description="업로드할 이미지 파일 (png, jpg 등)"
            )
        ],
        responses={201: ImageSerializer, 400: "파일 없음 오류", 500: "S3 연동 오류"}
    )
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
        # S3에 파일 저장 (동일 파일명 덮어쓰기 방지 리팩토링)
        ext = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = f"uploads/{unique_filename}"

        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=image_file.content_type,
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 업로드된 파일의 URL 생성
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        
        # DB에 저장
        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)


        return Response(serializer.data, status=status.HTTP_201_CREATED)

@require_http_methods(["GET"])
def get_post_detail(reqeust, id):
    try:
        post = Post.objects.get(id=id)
        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "user" : post.user.username
        }
        return JsonResponse({
            "status" : 200,
            "data": post_detail_json})
    except Post.DoesNotExist:
        raise PostNotFoundException