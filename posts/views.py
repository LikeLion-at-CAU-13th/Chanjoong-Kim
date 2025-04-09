from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods # 추가
from .models import * # 추가

import json

# Create your views here.

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello lielion-13th!"
        })
    

@require_http_methods(["GET"])
def get_post_detail(reqeust, id):
    post = get_object_or_404(Post, pk=id)
    post_detail_json = {
        "id" : post.id,
        "title" : post.title,
        "content" : post.content,
        "status" : post.status,
        "user" : post.user.username,
    }
    return JsonResponse({
        "status" : 200,
        "data": post_detail_json})

@require_http_methods(["POST", "GET"])
def post_list(request):
     if request.method == "POST":
    
        # byte -> 문자열 -> python 딕셔너리
        body = json.loads(request.body.decode('utf-8'))
    
		    # 프론트에게서 user id를 넘겨받는다고 가정.
		    # 외래키 필드의 경우, 객체 자체를 전달해줘야하기 때문에
        # id를 기반으로 user 객체를 조회해서 가져옵니다 !
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)

	    # 새로운 데이터를 DB에 생성
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            user = user
        )
    
	    # Json 형태 반환 데이터 생성
        new_post_json = {
            "id": new_post.id,
            "title" : new_post.title,
            "content": new_post.content,
            "status": new_post.status,
            "user": new_post.user.id
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 생성 성공',
            'data': new_post_json
        })
    
     # 게시글 전체 조회
     if request.method == "GET":
        post_all = Post.objects.all()
    
		# 각 데이터를 Json 형식으로 변환하여 리스트에 저장
        post_json_all = []
        
        for post in post_all:
            post_json = {
                "id": post.id,
                "title" : post.title,
                "content": post.content,
                "status": post.status,
                "user": post.user.id
            }
            post_json_all.append(post_json)

        return JsonResponse({
            'status': 200,
            'message': '게시글 목록 조회 성공',
            'data': post_json_all
        }) 

@require_http_methods(["GET","PATCH","DELETE"])
def post_detail(request, post_id):

    # post_id에 해당하는 단일 게시글 조회
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id)

        post_json = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "status": post.status,
            "user": post.user.id,
        }
        
        return JsonResponse({
            'status': 200,
            'message': '게시글 단일 조회 성공',
            'data': post_json
        })

    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))
        
        update_post = get_object_or_404(Post, pk=post_id)

        if 'title' in body:
            update_post.title = body['title']
        if 'content' in body:
            update_post.content = body['content']
        if 'status' in body:
            update_post.status = body['status']
    
        
        update_post.save()

        update_post_json = {
            "id": update_post.id,
            "title" : update_post.title,
            "content": update_post.content,
            "status": update_post.status,
            "user": update_post.user.id,
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 수정 성공',
            'data': update_post_json
        })
    
    if request.method == "DELETE":
        delete_post = get_object_or_404(Post, pk=post_id)
        delete_post.delete()

        return JsonResponse({
                'status': 200,
                'message': '게시글 삭제 성공',
                'data': None
        })
    
#특정 post의 모든 comment를 조회하기기
@require_http_methods(["GET"])
def check_comment(request, post_id):

    #post에 있는 댓글 즉 comment를 조회하기
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id)
        comments = Comment.objects.filter(post = post)
        
        #모든 comment를 json 형식의 dictionary로 받는다.
        comments_json_all = []

        #comments 내부의 값이 몇개인지 모르므로 아래와 같은 형태의 반복문을 사용
        #models.py 내부의 comment의 양식을 이용하자
        for c in comments:
            comment_json = {
                "c_id" : c.c_id,
                "author" : c.author,
                "body" : c.body,
                "written_time" : c.writen_time,
                "modified_time" : c.modified_time,
            }
            comments_json_all.append(comment_json) #모든 comment를 dictionary에 정리해서 넣어준다.

        return JsonResponse({
            'status' : 200,
            'message' : '특정한 post의 모든 comments 조회에 성공했습니다.',
            'date' : comments_json_all
        })

#카레고리 별로 게시글을 필터링해서 볼 수 있는 기능
@require_http_methods(["GET"])
def filter_post_by_category(request, category):
    if request.method == "GET":
        #Base_Model에 있는 생성 시각 가져와서 오름차순
        linker_cat_post = cat_post_linker.objects.filter(category_id = category).order_by('-post__created')
        post_filtered = [link.post for link in linker_cat_post] # 걸러진 post들을 위한 dictionary

        post_filtered_json_all = [] #모든 json을 dictionary로 받는다

        for fp in post_filtered : 
            post_filtered_json = {
                "id" : fp.id,
                "title" : fp.title,
                "content" : fp.content,
                "status" : fp.status,
                "user" : fp.user.id,
            }
            post_filtered_json_all.append(post_filtered_json)

        return JsonResponse({
            'status': 200,
            'message': '카테고리별 모든 post 조회',
            'date' : post_filtered_json_all
        })
