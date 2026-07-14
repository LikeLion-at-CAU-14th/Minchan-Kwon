### Model Serializer case
from django.utils import timezone

from config.custom_api_exceptions import PostConflictException
from rest_framework import serializers
from .models import Post, Comment, Image

class PostSerializer(serializers.ModelSerializer):

  class Meta:
    model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
    fields = "__all__"  # 모델에서 어떤 필드를 가져올지 >> 전체 필드

  def validate(self, data):
    title = data.get('title')
    if title and Post.objects.filter(title=title).exists():
      raise PostConflictException(detail=f"A post with title: '{title}' already exists.")
    
    writer = data.get('writer')  # 작성자 오브젝트
    if writer:
      today = timezone.now().date()  # 날짜 추출
      
      # DB에서 오늘 작성자가 썼던 글이 있는지 조회
      if Post.objects.filter(writer=writer, created_at__date=today).exists():
        raise serializers.ValidationError("게시글은 하루에 하나만 올릴 수 있습니다.")
    
    return data

class CommentSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Comment
    fields = ['id', 'post', 'content']

  def validate_content(self, value):
    # len() 함수로 글자 수 검사
    if len(value) < 15:
      # 15자 안 되면 DRF 예외를 통해 백엔드 문 닫음
      raise serializers.ValidationError("댓글은 최소 15자 이상 작성해야합니다.")
    
    # 15자 이상이면 통과
    return value

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
