from django.urls import path
from posts.views import *

urlpatterns = [
    #path('', hello_world, name = 'hello_world'),
    #path('<int:id>', get_post_detail), # 추가
    #path("page", index, name="my-page"),
    path('', post_list, name="post_list"),
    path('<int:post_id>/', post_detail, name='post_detail'), # Post 단일 조회
    path('comment/<int:post_id>/', check_comment, name="check_comment"), # 특정 comment를 조회하기
    path('filter/<int:category>/', filter_post_by_category, name="filter_post_by_category")
]