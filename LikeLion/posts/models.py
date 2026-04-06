from django.db import models
from accounts.models import User
from django.conf import settings

# Create your models here.

# 추상 클래스 정의
class BaseModel(models.Model): # models.Model을 상속받음
    created_at = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장
    updated_at = models.DateTimeField(auto_now=True) # 객체를 저장할 때 날짜와 시간 갱신

    class Meta:
        abstract = True

#카테고리 모델
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    # 누락되었던 def __str__(self): 메서드 추가하였습니다.
    def __str__(self):
        return self.name

class Post(BaseModel): # BaseModel을 상속받음
    CHOICES = (
        ('STORED', '보관'),
        ('PUBLISHED', '발행')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=CHOICES, default='STORED')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    # 게시글에서 카테고리와의 연결을 위해 Post class에 categories 필드를 ManyToMany로 연결
    # 다대다관계이기에 하나의 게시글은 여러 개의 카테고리에 속할 수 있고, 게시글이 삭제되어도 카테고리는 삭제되지 않음
    categories = models.ManyToManyField(Category, related_name='posts')

    def __str__(self):
        return self.title
    
# 댓글 모델    
class Comment(BaseModel): # 작성 시간과 수정 시간을 저장하기 위해 BaseModel class를 상속
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # 하나의 게시글에 여러개의 댓글이 달릴 수 있어야 하니 다대일 관계를 만들어주는 models.ForeignKey 사용
    # 게시글이 삭제되면 댓글도 삭제되어야 하니 CASCADE
    content = models.TextField()

    # 누락되었던 def __str__(self): 메서드 추가하였습니다.
    def __str__(self):
        return f"Comment {self.id} on {self.post.title}"