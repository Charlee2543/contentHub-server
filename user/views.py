from django.shortcuts import render
from rest_framework.views import APIView
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer,LoginSerializer,EditProfile
from .models import User
from django.shortcuts import get_object_or_404
from decouple import config



from rest_framework_simplejwt.settings import api_settings

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
   def put(self, request):
      target_uuid = request.data.get('uuid')
      user = get_object_or_404(User, user_id=target_uuid) # คือ ฟังก์ชัน helper ที่ Django มีมาให้ ใช้สำหรับ ไป ค้นหา object ใน database จาก model ที่ระบุ ถ้าเจอ → return object ออกมา ถ้าไม่เจอ → return HTTP 404 Error (Http404) อัตโนมัติ
      # partial=True → validate เฉพาะ field ที่ส่งมา
      # print('user: ', user)
      serializer = EditProfile(user, data=request.data, partial=True) #partial=True หมายความว่า DRF จะ validate เฉพาะ field ที่ส่งมา
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

            """ access_token ไปหน้าบ้าน เก็บ refresh_token ไว้ที่ cookie  """

            # ✅ สร้าง JWT token
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # ✅ สร้าง response + set cookie refresh
            resp = Response({
               'message': 'Login successful',
               'access': str(access),
               'user_id': user.user_id,
               'email': user.email,
               'username': user.username,
               'profile_picture_url': user.profile_picture_url,
               'updated_at': user.updated_at,
               'created_at': user.created_at,
            }, status=status.HTTP_200_OK)

            max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
            resp.set_cookie(
               "refresh",
               str(refresh),
               # httponly=True,
               # secure=config("Token_Secure"),#dev: ตั้ง secure=False เฉพาะใน local dev local ต้อง False
               #secure=True,#secure=True หมายถึง cookie จะถูกเก็บ เฉพาะเมื่อ request ใช้ HTTPS
               samesite="Lax",
               max_age=max_age,
               # path="/user/token/refresh/"
               path="/"
            )
            return resp
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
      def validate(self, attrs):
         refresh = RefreshToken(attrs['refresh'])
         data = {'access': str(refresh.access_token)}

         if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
            if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION'):
               try:
                  refresh.blacklist()
               except AttributeError:
                  pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data['refresh'] = str(refresh)

         return data


class RefreshTokenCookieView(TokenRefreshView):
   serializer_class = CustomTokenRefreshSerializer  # ใช้ custom serializer
   
   def post(self, request, *args, **kwargs):
         refresh = request.COOKIES.get("refresh")
         #ดึง COOKIES จาก application ที่ชื่อ refresh
         if not refresh:
            return Response({"detail":"no refresh cookie"}, status=status.HTTP_401_UNAUTHORIZED)
         serializer = self.get_serializer(data={"refresh": refresh})
         #ดึง data COOKIES จาก application ที่ชื่อ refresh ออกมาเป็น object data={'refresh': ''}
         # serializer.is_valid(raise_exception=True)
         #  validate refresh token
         try:
            # Decode refresh token เพื่อดึง user_id
            refresh_token = RefreshToken(refresh)
            # print('refresh_token: ', refresh_token)
            user_id = refresh_token.payload.get("user_id")
            
            # print('user_id from token: ', user_id)
            
            if not user_id:
               return Response({"detail": "Invalid token: no user_id"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # ตรวจสอบว่า user_id นี้มีอยู่ในฐานข้อมูลหรือไม่
            try:
               user = User.objects.get(user_id=user_id)
               print(f'User found: {user.username}')
            except User.DoesNotExist:
               return Response({"detail": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)
               
            # ตรวจสอบว่า user ยังใช้งานได้หรือไม่
            if not user.is_active:
               return Response({"detail": "User account is disabled"}, status=status.HTTP_401_UNAUTHORIZED)
               
         except TokenError as e:
            print(f'Token error: {e}')
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

         # ถ้าผ่านการตรวจสอบแล้ว ดำเนินการ refresh token ตามปกติ
         # serializer = self.get_serializer(data={"refresh":refresh})

         # try:
         #    serializer = self.get_serializer(data={"refresh": refresh_token_str})
         #    serializer.is_valid(raise_exception=True)
         #    data = serializer.validated_data  # contains access and maybe refresh (if rotate)
         # except Exception:
         #    return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
         
         #  validate refresh token
         # serializer = self.get_serializer(data={"refresh":refresh})
         serializer.is_valid(raise_exception=True)
         data = serializer.validated_data  # contains access and maybe refresh (if rotate)
         print('data: ', data)
         access = data.get("access")
         new_refresh = data.get("refresh", None)
         resp = Response({
            "access": access,
            "user_id": user_id,  # ส่ง user_id กลับไปด้วย (optional)
            "username": user.username  # ส่ง username กลับไปด้วย (optional)
         })
         if new_refresh:
            max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
            resp.set_cookie(
            "refresh",
            new_refresh,
            # httponly=True, 
            # secure= config("Token_Secure"),#dev: ตั้ง secure=False เฉพาะใน local dev local ต้อง False
            #secure=True,#secure=True หมายถึง cookie จะถูกเก็บ เฉพาะเมื่อ request ใช้ HTTPS
            samesite="Lax",
            max_age=max_age,
            path="/")

         return resp

class LogoutView(APIView):
   def post(self, request):
      resp = Response({"detail": "logged out"}, status=status.HTTP_200_OK)

      resp.delete_cookie(
            key="refresh",
            path="/",
            domain="localhost",      # หรือถ้า set domain="localhost" ต้องใส่ตรงนี้ผ
            samesite="Lax",
      )
      return resp