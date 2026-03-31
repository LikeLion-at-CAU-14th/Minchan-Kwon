from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import *

# Create your views here.
@require_http_methods(["GET"])
def get_post_detail(request, id):
    # N + 1 문제를 해결해주는 prefetch_related 키워드를 적용하였습니다.
    post = get_object_or_404(Post.objects.prefetch_related('comments', 'categories'), pk=id)

    # 게시글에 달린 댓글 리스트와 카테고리 정보를 함께 응답할 수 있는 코드를 추가하였습니다.
    comments = post.comments.all()
    comment_list = []

    for comment in comments:
        comment_list.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),           
        })

    categories = post.categories.all()
    category_list = []

    for category in categories:
        category_list.append({
            "id": category.id,
            "name": category.name,
        })

    post_detail_json = {
        "id" : post.id,
        "title" : post.title,
        "content" : post.content,
        "status" : post.status,
        "writer" : post.writer.username,
        # API에 작성일과 수정일을 추가하였습니다. 
        "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        # 게시글에 달린 댓글 리스트와 카테고리 정보 추가하였습니다.
        "categories": category_list,
        "comments": comment_list,
    }
    return JsonResponse({
        "status" : 200,
        "data": post_detail_json})

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello likelion-14th!"
        })
def index(request):
    return render(request, 'index.html')