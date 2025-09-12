from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from .models import Comment
# from postArticies.models import Articles
from .serializers import CommentSerializer, CommentCreateSerializer
# Create your views here.
class CommentPost(APIView):
   # permission_classes = [IsAuthenticated] # เช็ค aeccessToken
   """
   API View สำหรับ:
   GET: ดึงรายการ comments
   POST: สร้าง comment ใหม่
   """
   # กำหนด permission - อ่านได้ทุกคน, เขียนได้เฉพาะคนที่ login
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   def get(self, request):
      """
      GET /api/comments/?article_id=1&type=main&parent_id=1
      ดึงรายการ comments พร้อม filter options
      """
      # ดึง comments ที่ active พร้อม related data เพื่อลด database queries
      queryset = Comment.objects.filter(status='active').select_related('user', 'article', 'parent')
      
      # Filter by article_id ถ้ามีการส่งมา
      article_id = request.query_params.get('article_id')
      if article_id:
            queryset = queryset.filter(article_id=article_id)
            
      # Filter by type (main comments หรือ replies)
      comment_type = request.query_params.get('type', 'main')
      print('comment_type: ', request.query_params.get)
      if comment_type == 'main':
            # เฉพาะ main comments (parent=None) พร้อม prefetch replies
            queryset = queryset.filter(parent=None).prefetch_related(
               # Prefetch replies ที่ active พร้อม user data
               Prefetch('replies', queryset=Comment.objects.filter(status='active').select_related('user'))
            )
      elif comment_type == 'replies':
            # เฉพาะ replies ของ parent ที่ระบุ
            parent_id = request.query_params.get('parent_id')
            if parent_id:
               queryset = queryset.filter(parent_id=parent_id)

      # เรียงจากใหม่ไปเก่า
      queryset = queryset.order_by('-created_at')#[3:5]#limit
      
      # Serialize data และส่งกลับ
      serializer = CommentSerializer(queryset, many=True)
      return Response(serializer.data)

   def post(self, request):

        """
        POST /api/comments/
        สร้าง comment ใหม่
        """
        print('request: ', request)
        print('self: ', self)
        # ใช้ CommentCreateSerializer สำหรับ validation        
        serializer = CommentCreateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # บันทึกลง database
            comment = serializer.save()
            
            # ส่งกลับ comment ที่สร้างใหม่ในรูปแบบ CommentSerializer
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
      
      # ถ้า validation ผิด ส่งกลับ errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentByArticleView(APIView):
    """
    API View สำหรับดึง comments ทั้งหมดของ article
    GET /api/comments/by-article/?article_id=1
    """
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    print('CommentByArticleView')

    def get(self, request):
        """
        ดึง comments ทั้งหมดของ article พร้อม replies
        """
        article_id = request.query_params.get('article_id')
        print('article_id: ', article_id)
        if not article_id:
            return Response({'error': 'article_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        print('main_comments')
      # ดึง main comments พร้อม replies แบบ optimized
        main_comments = Comment.objects.filter(
            article_id=article_id,     # filter by article
            parent=None,               # เฉพาะ main comments
            status='active'            # เฉพาะที่ active
        ).select_related('user').prefetch_related(
            # Prefetch replies พร้อม user data เรียงตามวันที่
            Prefetch('replies',queryset=Comment.objects
                                        .filter(status='active')
                                        # .select_related('user')
                                        .order_by('created_at'))
        ).order_by('-created_at')  # main comments เรียงจากใหม่ไปเก่า
        print('main_comments: ', main_comments)
        
        serializer = CommentSerializer(main_comments, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK)

class CommentReplyView(APIView):
    """
    API View สำหรับ reply comment
    POST /api/comments/{comment_id}/reply/
    """
    permission_classes = [permissions.IsAuthenticated]  # ต้อง login ถึงจะ reply ได้

    def post(self, request, comment_id):
        """
        ตอบกลับ comment ที่ระบุ
        """
        try:
            # หา parent comment
            parent_comment = Comment.objects.get(id=comment_id, status='active')
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # ตรวจสอบว่าไม่ใช่ reply ต่อ reply
        if parent_comment.parent:
            return Response(
                {'error': 'Cannot reply to a reply'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate ข้อมูลที่ส่งมา
        serializer = CommentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # บันทึก reply พร้อมกำหนด parent และ article
            reply = serializer.save(parent=parent_comment, article=parent_comment.article)
            
            # ส่งกลับ reply ที่สร้างใหม่
            response_serializer = CommentSerializer(reply)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# urls.py - เปลี่ยนจาก Router เป็น path แบบปกติ