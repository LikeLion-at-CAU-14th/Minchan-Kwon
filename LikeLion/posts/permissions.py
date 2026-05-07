from rest_framework import permissions
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