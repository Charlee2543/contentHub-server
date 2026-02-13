# app_name/serializers.py

import re
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = '__all__' # หรือระบุ fields ที่ต้องการ
      # validate เฉพาะ field บังคับใน POST
      username = serializers.CharField(required=True, max_length=100)
      email = serializers.EmailField(required=True)
      password = serializers.CharField(write_only=True, required=True, min_length=6)

   def validate_username(self, value):
      """Validate username field"""
      print('validate_username')
      if len(value) < 3:
            raise serializers.ValidationError("Username ต้องมีอย่างน้อย 3 ตัวอักษร")
      return value
   
   def validate_email(self, value):
      print('validate_email')
      """Validate email field"""
      if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email นี้ถูกใช้แล้ว")
      return value


   def create(self, validated_data):
      """สร้าง user ใหม่พร้อม hash password"""
      user = User(
            username=validated_data['username'],
            email=validated_data['email']
      )
      user.set_password(validated_data['password'])  # hash password
      user.save()
      return user

   def update(self, instance, validated_data):
      """อัพเดท user พร้อมจัดการ password"""
      if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
      
      for attr, value in validated_data.items():
            setattr(instance, attr, value)
      
      instance.save()
      return instance


   def validate(self, data):
      print('validate UserSerializer')
      # สามารถเพิ่ม logic เพิ่มได้ เช่น password strength
      return data
   

class LoginSerializer(serializers.Serializer):
   email = serializers.CharField()
   # print('email: ', email)
   password = serializers.CharField()
   # print('password: ', password)

   def validate(self, data):
      # print('self: ', self)
      email = data.get('email')
      # print('username: ', email)
      password = data.get('password')
      # print('password: ', password)
      
      if email and password:
            try:
               user = User.objects.get(email=email)
               if not user.check_password(password):
                  raise serializers.ValidationError("Invalid credentials (password)") #raise คือเงือนไขเป็นจริงจะโยน error ออกมา
               data['user'] = user
            except User.DoesNotExist:
               raise serializers.ValidationError("Invalid credentials (email)")
      else:
            raise serializers.ValidationError("Must include username and password")
      
      return data
   
class EditProfile (serializers.Serializer):
   user_id = serializers.CharField(required=True)
   username = serializers.CharField(required=True)
   email = serializers.CharField(required=True)
   profile_picture_url= serializers.CharField(required=True)
   created_at= serializers.CharField(required=True)
   updated_at= serializers.CharField(required=True)
   def validate_username(self, value):
      """Validate username field"""
      responseError=[]
      if len(value) < 3:
            # raise serializers.ValidationError("Username ต้องมีอย่างน้อย 3 ตัวอักษร")
            responseError.append("Username ต้องมีอย่างน้อย 3 ตัวอักษร")
      if not re.match(r'^[a-zA-Z0-9]+$', value):
         responseError.append("Username ต้องเป็นตัวอักษรภาษาอังกฤษหรือตัวเลขเท่านั้น")
      print('responseError: ', responseError)
      if responseError:
         raise serializers.ValidationError(responseError)
      return value
   
   def validate_email(self, value):
      print('validate_email')
      """Validate email field"""
      # print('self: ', self)
      userUuid=self.initial_data.get('uuid')
      # print('uuid: ', userUuid)
      oldEmail=User.objects.get(user_id=userUuid).email
      # print('oldEmail: ', oldEmail)
      responseError=[]
      #หรือใช้อันนี้ได้ if User.objects.filter(email=value).exclude(user_id=userUuid).exists():
      if User.objects.filter(email=value).exists():
         # print('value!=oldEmail: ', value!=oldEmail)
         if value!=oldEmail:
            responseError.append("Email นี้ถูกใช้แล้ว")
      if not re.match(r'^[a-zA-Z0-9@._-]+$', value):
         responseError.append("Email ใช้ตัวอักษรได้แค่ a-z,A-Z,0-9,@,.,_,- เท่านั้น")
      if responseError:
         raise serializers.ValidationError(responseError)
      return value
   
   def update(self, instance, validated_data):
      print('self: ', self)
      print('instance: ', instance)
      print('validated_data: ', validated_data)
      # instance คือ object 'user' ที่ส่งมาจาก View
      # validated_data คือ ข้อมูลที่ผ่านการตรวจสอบแล้ว
      
      instance.email = validated_data.get('email', instance.email)
      instance.username = validated_data.get('username', instance.username)
      # ปกติ user_id มักจะไม่ให้แก้ แต่ถ้าจะแก้ก็ใส่แบบเดียวกันครับ
      # instance.user_id = validated_data.get('user_id', instance.user_id)
      
      instance.save() # บันทึกลง Database
      return instance