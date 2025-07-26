### Model Serializer case

from rest_framework import serializers
from .models import Post, Comment
from .models import Image
from config.custom_api_exceptions import PostConflictException, PostValidationException, CommentValidationException, DailyPostLimitException # 13주차 실습
from django.utils import timezone
from datetime import datetime, timedelta


class PostSerializer(serializers.ModelSerializer):

  class Meta:
		# 어떤 모델을 시리얼라이즈할 건지
    model = Post
		# 모델에서 어떤 필드를 가져올지
		# 전부 가져오고 싶을 때
    fields = "__all__"

  # 필수 필드를 명시적으로 정의
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # 필수 필드 설정
    self.fields['title'].required = True
    self.fields['content'].required = True
    self.fields['user'].required = True
    # status는 기본값(STORED)이 있으므로 선택사항
    self.fields['status'].required = False

  # 개별 필드 validation
  def validate_title(self, value):
    if not value or not value.strip():
      raise serializers.ValidationError("제목은 필수 항목입니다.")
    
    if len(value.strip()) < 2:
      raise serializers.ValidationError("제목은 최소 2글자 이상이어야 합니다.")
    
    if len(value) > 100:
      raise serializers.ValidationError("제목은 100글자를 초과할 수 없습니다.")
    
    return value.strip()

  def validate_content(self, value):
    if not value or not value.strip():
      raise serializers.ValidationError("내용은 필수 항목입니다.")
    
    if len(value.strip()) < 5:
      raise serializers.ValidationError("내용은 최소 5글자 이상이어야 합니다.")
    
    return value.strip()

  def validate_status(self, value):
    # Post 모델에 정의된 실제 choices 사용
    valid_statuses = ['STORED', 'PUBLISHED']
    if value not in valid_statuses:
      raise serializers.ValidationError(f"상태는 {', '.join(valid_statuses)} 중 하나여야 합니다. (STORED: 보관, PUBLISHED: 발행)")
    
    return value

  # 중복된 게시글 제목이 있다면 예외 발생, 13주차 실습
  # validate 메서드는 시리얼라이저의 유효성 검사 단계에서 호출됨
  def validate(self, data):
    print(f"Validating data: {data}")  # 디버깅용
    
    # 하루 게시글 작성 제한 검사 (새 게시글 작성 시에만)
    if not self.instance:  # 새 게시글 작성 시에만 체크 (업데이트가 아닌 경우)
      user = data.get('user')
      if user:
        # 오늘 00:00:00부터 현재까지의 시간 범위
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # 오늘 해당 사용자가 작성한 게시글 개수 확인
        today_posts_count = Post.objects.filter(
          user=user,
          created__gte=today_start,
          created__lt=today_end
        ).count()
        
        print(f"User {user} has written {today_posts_count} posts today")  # 디버깅용
        
        if today_posts_count >= 1:
          raise DailyPostLimitException(user=user.username if hasattr(user, 'username') else str(user))
    
    # 제목 중복 검사 (업데이트 시에는 자기 자신 제외)
    title = data.get('title')
    if title:
      existing_posts = Post.objects.filter(title=title)
      
      # 업데이트인 경우 현재 인스턴스 제외
      if self.instance:
        existing_posts = existing_posts.exclude(id=self.instance.id)
      
      if existing_posts.exists():
        raise PostConflictException(detail=f"'{title}' 제목의 게시글이 이미 존재합니다.")
    
    # 모든 필수 필드 검사 (이 부분이 중요!)
    required_fields = ['title', 'content', 'user']
    missing_fields = []
    
    for field in required_fields:
      if field not in data or not data[field]:
        missing_fields.append(field)
    
    if missing_fields:
      field_mapping = {
        'title': '제목',
        'content': '내용', 
        'user': '사용자'
      }
      missing_korean_fields = [field_mapping.get(f, f) for f in missing_fields]
      raise serializers.ValidationError(f"다음 필드들이 누락되었습니다: {', '.join(missing_korean_fields)}")
    
    return data

# comment를 가져오는 시리얼라이져
class CommentSerializer(serializers.ModelSerializer):

  class Meta:
    model = Comment
    fields = "__all__"

  # 필수 필드를 명시적으로 정의
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # 필수 필드 설정
    self.fields['author'].required = True
    self.fields['body'].required = True
    self.fields['post'].required = True

  # 댓글 내용 validation - 최소 15자 이상
  def validate_body(self, value):
    if not value or not value.strip():
      raise serializers.ValidationError("댓글 내용은 필수 항목입니다.")
    
    # 공백 제거 후 길이 체크
    cleaned_value = value.strip()
    if len(cleaned_value) < 15:
      raise serializers.ValidationError(f"댓글은 최소 15자 이상 작성해야 합니다. (현재: {len(cleaned_value)}자)")
    
    if len(cleaned_value) > 500:
      raise serializers.ValidationError("댓글은 500자를 초과할 수 없습니다.")
    
    return cleaned_value

  # 작성자 validation
  def validate_author(self, value):
    if not value or not value.strip():
      raise serializers.ValidationError("작성자명은 필수 항목입니다.")
    
    cleaned_value = value.strip()
    if len(cleaned_value) < 2:
      raise serializers.ValidationError("작성자명은 최소 2글자 이상이어야 합니다.")
    
    if len(cleaned_value) > 30:
      raise serializers.ValidationError("작성자명은 30글자를 초과할 수 없습니다.")
    
    return cleaned_value

  # 전체 validation
  def validate(self, data):
    print(f"Validating comment data: {data}")  # 디버깅용
    
    # 모든 필수 필드 검사
    required_fields = ['author', 'body', 'post']
    missing_fields = []
    
    for field in required_fields:
      if field not in data or not data[field]:
        missing_fields.append(field)
    
    if missing_fields:
      field_mapping = {
        'author': '작성자',
        'body': '댓글 내용',
        'post': '게시글'
      }
      missing_korean_fields = [field_mapping.get(f, f) for f in missing_fields]
      raise serializers.ValidationError(f"다음 필드들이 누락되었습니다: {', '.join(missing_korean_fields)}")
    
    return data

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"