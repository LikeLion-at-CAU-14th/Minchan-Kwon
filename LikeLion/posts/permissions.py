from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.utils import timezone


class TimeRestrictedPermission(permissions.BasePermission):
    message = "22:00 ~ 07:00 사이에는 게시판 이용이 제한됩니다."

    def has_permission(self, request, view):
        now = timezone.now()
        if now.hour >= 22 or now.hour <= 7:
            return False
        
        else:
            return True
        
class IsAuthorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.writer == request.user
    
class IsAvailableTime(BasePermission):
    def has_permission(self, request, view):
        # 💡 여기에 멋사 과제 조건에 맞는 시간 제한 로직이 들어가야 합니다.
        # 일단 서버가 켜지게 하려면 무조건 True를 반환하게 만드세요!
        return True 

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.writer == request.user