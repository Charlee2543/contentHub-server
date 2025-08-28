# Create your models here.
from django.db import models
import uuid
from django.utils import timezone
import pytz
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
   user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   username = models.CharField(max_length=100, unique=True)
   email = models.EmailField(max_length=255, unique=True)
   password = models.CharField(max_length=255)
   profile_picture_url = models.TextField(blank=True, null=True)
   is_active = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   def save(self, *args, **kwargs):
      """Override save method เพื่อให้เวลาเป็น Asia/Bangkok timezone"""
      bangkok_tz = pytz.timezone("Asia/Bangkok")
      current_time = timezone.now().astimezone(bangkok_tz)
      
      if not self.pk:  # ถ้าเป็นการสร้างใหม่
            self.created_at = current_time
      self.updated_at = current_time
      
      super().save(*args, **kwargs)
   
   class Meta:
      managed = False  # สำคัญมาก! บอก Django ว่าตารางนี้ถูกจัดการโดย Database
      db_table = 'users' # กำหนดชื่อตารางใน PostgreSQL 
      
   def set_password(self, raw_password):
      """Hash password ด้วย bcrypt"""
      # วิธีที่ 1: ใช้ Django's make_password (แนะนำ)
      self.password = make_password(raw_password)
      
      # วิธีที่ 2: ใช้ bcrypt โดยตรง
      # salt = bcrypt.gensalt()
      # self.password = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

   def check_password(self, raw_password):
      """ตรวจสอบ password"""
      # วิธีที่ 1: ใช้ Django's check_password (แนะนำ)
      return check_password(raw_password, self.password)

      # วิธีที่ 2: ใช้ bcrypt โดยตรง
      # return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))   