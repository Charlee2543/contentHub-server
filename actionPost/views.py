from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class CommentPost(APIView):
   permission_classes = [IsAuthenticated] 
   def get(self,repuest):
         return Response({"status": "success", "message":"test get comment success "}, status=status.HTTP_200_OK)
      # try:
      #    Response({"test get comment success "}, status=status.HTTP_200_OK)
      # except:
      #    Response({"test get comment success "}, status=status.HTTP_404_NOT_FOUND)