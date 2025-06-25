from django.db import models
from accounts.models import User

# Create your models here.
# 추상 클래스 정의
class BaseModel(models.Model): # models.Model을 상속받음
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장
    updated = models.DateTimeField(auto_now=True) # 객체를 저장할 때 날짜와 시간 갱신

    class Meta:
        abstract = True # 추상 클래스


class Post(BaseModel): # BaseModel을 상속받음

    CHOICES = (
        ('STORED', '보관'),
        ('PUBLISHED', '발행')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    status = models.CharField(max_length=15, choices=CHOICES, default='STORED')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')

    def __str__(self):
        return self.title
    
class Comment(BaseModel): # 댓글 기능, 댓글 사용자의 id는 따로 입력 받는다.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = 'comment')
    c_id = models.AutoField(primary_key = True)
    author = models.CharField(max_length = 30)
    body = models.TextField()
    writen_time = models.DateTimeField(auto_now_add = True)
    modified_time = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.body
    
class Category(BaseModel):
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=30)

    def __str__(self):
        return self.cat_name
    
class cat_post_linker(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='linked_post')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='linked_cat')
    
    def __str__(self): # 제목 - 카테고리 쌍으로 만들기
        return f'{self.post.title} - {self.category.cat_name}'
    
class Image(BaseModel):
    id = models.AutoField(primary_key=True)
    image_url = models.URLField(max_length=500)  # S3에 업로드된 이미지의 URL 저장

    def __str__(self):
        return f"Image {self.id}"