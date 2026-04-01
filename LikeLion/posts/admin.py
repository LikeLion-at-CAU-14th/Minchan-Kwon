from django.contrib import admin
from .models import Post, Comment, Category

# Register your models here.

# [수정] Post 는 아래에서 @admin.register 로 등록하므로 여기서는 제외합니다.
admin.site.register(Comment)
admin.site.register(Category)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'writer', 'status', 'created_at')  # 관리자 목록에 노출될 필드
    search_fields = ('title', 'content')    # 검색 기능 추가