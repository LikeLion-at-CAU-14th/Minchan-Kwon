from django.urls import path
from posts.views import *

urlpatterns = [
 #   path('', hello_world, name = 'hello_world'),
 #   path('page', index, name='my-page'),
 #   path('<int:id>', get_post_detail)

    path('<int:post_id>', post_detail, name = "post_detail"),
    path('<int:post_id>/comments', comment_list, name = "comment_list"),
    path('categories/<int:category_id>', category_detail, name="category_posts"),
    path('', post_list, name = "post_list")
]