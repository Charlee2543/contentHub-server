from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Articles
from .serializers import PostSerializer
# Create your views here.
class PostListAPIView(APIView):
    def get(self, request):
        print("Start get data")
        # ดึงข้อมูลจาก database
        posts = Articles.objects.order_by('created_at')[0:10]
        # Post.objects.all() ดึงข้อมูลทั้งหมดจาก table
        # print("posts =  ", {posts})
        # แปลง object ที่ได้่เป็น json
        serializer = PostSerializer(posts, many=True)
        # print("serializer =  ", {serializer})
        return Response(serializer.data)  
    
    def post(self, request):
        # print("Start creating data")
        # print(request.data)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class PostDetailAPIView(APIView):
    """API สำหรับจัดการบทความเฉพาะ ID"""
    
    def get(self, request, article_id):
        """ดึงบทความเฉพาะ ID"""
        print(f"Getting article with ID: {article_id}")
        try:
            # get_object_or_404 จะ raise Http404 หากไม่เจอข้อมูล
            article = get_object_or_404(Articles, article_id=article_id)
            # article = Articles.objects.filter(article_id=article_id).values()
            serializer = PostSerializer(article)
            return Response(serializer.data)            

        except Articles.DoesNotExist:
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    def put(self, request, article_id):
        """Update ทั้งหมดของบทความ"""
        print(f"Updating entire article with ID: {article_id}")
        try:
            article = get_object_or_404(Articles, article_id=article_id)
            # ไม่ใส่ partial=True หมายความว่าต้องส่งข้อมูลครบทุกฟิลด์
            serializer = PostSerializer(article, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Articles.DoesNotExist:
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    def delete(self, request, article_id):
        """ลบบทความ"""
        print(f"Deleting article with ID: {article_id}")
        try:
            article = get_object_or_404(Articles, article_id=article_id)
            article_title = article.title  # เก็บชื่อเพื่อแสดงใน message
            article.delete()
            return Response(
                {
                    'message': f'Article "{article_title}" deleted successfully',
                    'deleted_id': article_id
                }, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Articles.DoesNotExist:
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )