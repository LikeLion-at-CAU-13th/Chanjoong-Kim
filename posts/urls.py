from django.urls import path
from posts.views import *

urlpatterns = [
    #path('', hello_world, name = 'hello_world'),
    #path('<int:id>', get_post_detail), # 13주차 실습용
    #path("page", index, name="my-page"),
    #path('', post_list, name="post_list"),
    #path('<int:post_id>/', post_detail, name='post_detail'), # Post 단일 조회

    path('', PostList.as_view()), # post 전체 조회
    path('<int:post_id>/', PostDetail.as_view()), # post 개별 조회, 13주차 실습

    # 댓글 관련 URL 패턴
    path('comments/', CommentList.as_view(), name='comment-list'),  # 댓글 전체 조회/생성
    path('comments/<int:comment_id>/', CommentDetail.as_view(), name='comment-detail'),  # 댓글 상세 조회
    path('<int:post_id>/comments/', PostCommentList.as_view(), name='post-comment-list'),  # 특정 게시글의 댓글 목록

    #path('comment/<int:post_id>/', check_comment, name="check_comment"), # 특정 comment를 조회하기
    path('filter/<int:category>/', filter_post_by_category, name="filter_post_by_category"),
    path('upload/', ImageUploadView.as_view(), name='image-upload')

]