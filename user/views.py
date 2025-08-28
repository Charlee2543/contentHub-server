from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer,LoginSerializer
from .models import User
from django.shortcuts import get_object_or_404

# Create your views here.
class UserAPIView(APIView):
   def get(self,request):
      posts = User.objects.all()
      # แปลง object ที่ได้่เป็น json
      serializer = UserSerializer(posts, many=True)
      # print('serializer: ', serializer)
      return Response(serializer.data, status=status.HTTP_200_OK)
   def post(self, request):
      # print(request.data)
      serializer = UserSerializer(data=request.data)
      # print('serializer: ', serializer)
      if serializer.is_valid(raise_exception=True): # validate ทุก field
            print("ข้อมูลที่ validate แล้ว:", serializer.validated_data)
            user =serializer.save()
            return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserEditProfile(APIView):
# PUT (แก้ไข user)
   def put(self, request, pk):
      print('pk: ', pk)
      user = get_object_or_404(User, user_id=pk) # คือ ฟังก์ชัน helper ที่ Django มีมาให้ ใช้สำหรับ ไป ค้นหา object ใน database จาก model ที่ระบุ ถ้าเจอ → return object ออกมา ถ้าไม่เจอ → return HTTP 404 Error (Http404) อัตโนมัติ
      # partial=True → validate เฉพาะ field ที่ส่งมา
      serializer = UserSerializer(user, data=request.data, partial=True) #partial=True หมายความว่า DRF จะ validate เฉพาะ field ที่ส่งมา
      if serializer.is_valid(raise_exception=True):
         serializer.save()   # update เฉพาะ field ที่เปลี่ยนแปลง
         return Response(serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

class LoginAPIView(APIView):
   """API สำหรับเข้าสู่ระบบ"""
   
   def post(self, request):
      """เข้าสู่ระบบ"""
      serializer = LoginSerializer(data=request.data)
      if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            return Response({
               'message': 'Login successful',
               'token': 'token',
               'user_id': user.user_id,
               'username': user.username,
               'profile_picture_url': user.profile_picture_url,
               'email': user.email
            }, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)