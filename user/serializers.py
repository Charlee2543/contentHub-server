# app_name/serializers.py

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
   print('email: ', email)
   password = serializers.CharField()
   print('password: ', password)

   def validate(self, data):
      print('self: ', self)
      email = data.get('email')
      print('username: ', email)
      password = data.get('password')
      print('password: ', password)
      
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