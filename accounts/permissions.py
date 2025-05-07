from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import datetime, time
from rest_framework.exceptions import PermissionDenied

class IsAllowedTime(BasePermission):
    # 22:00 ~ 명일 07:00까지 차단하기

    def has_permission(self, request, view):
        now = datetime.now().time() #접속 시각을 받음
        block_start = time(22,0)
        block_end = time(7,0)

        if now >= block_start or now <= block_end:
            raise PermissionDenied(detail = '접근 제한 시각 (22:00 ~ 07:00)')
        return True

# SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS'), ReadOnly 형태의 튜플 상수
class IsOwnerOrReadOnly(BasePermission):
    # 작성자만 수정 가능 그 외의 사람은 읽기만 가능

    def has_object_permission(self, request, view, obj):
        # 읽기 전용 API만 허용
        if request.method in SAFE_METHODS:
            return True
        
        # 그렇지 않은 경우 작성자와 ID 비교, 같으면 true, 다르면 False를 돌려줌
        if obj.user == request.user:
            return True
            
        raise PermissionDenied("작성자만이 권한을 행사할 수 있습니다.")
