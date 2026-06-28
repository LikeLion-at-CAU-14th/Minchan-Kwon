from django.urls import path, include
from posts.views import *

urlpatterns = [
 #   path('', hello_world, name = 'hello_world'),
 #   path('page', index, name='my-page'),
 #   path('<int:id>', get_post_detail)

    # path('<int:post_id>', post_detail, name = "post_detail"),
    # path('<int:post_id>/comments', comment_list, name = "comment_list"),
    # path('categories/<int:category_id>', category_detail, name="category_posts"),
    # path('', post_list, name = "post_list")

    path('', PostList.as_view()), # post 전체 조회
    path('<int:post_id>/', PostDetail.as_view()), # post 개별 조회
    path('<int:post_id>/comments/' , CommentList.as_view() , name='comment-list'),
    path('<int:post_id>/comments/<int:comment_id>/' , CommentDetail.as_view() , name='comment-detail'),

    path('upload/', ImageUploadView.as_view(), name='image-upload')
]