from django.db import models
from django.core.exceptions import ValidationError
from postArticies.models import Articles
from user.models import User
import pytz 
from django.utils import timezone

class Comment(models.Model):
   def default_thai_time():
      return timezone.now().astimezone(pytz.timezone("Asia/Bangkok"))
   # ตัวเลือกสำหรับสถานะของ comment
   STATUS_CHOICES = [
      ('active', 'Active'),      # comment ปกติ
      ('deleted', 'Deleted'),    # comment ที่ถูกลบ
      ('hidden', 'Hidden'),      # comment ที่ถูกซ่อน
   ]
   
   # ความสัมพันธ์กับ Article, related_name='comments' 
   # ทำให้เรียก article.comments.all() ได้
   article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name='comments')
   
   # ความสัมพันธ์กับ User (คนที่เขียน comment)
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   
   # Self-referencing ForeignKey สำหรับ reply system
   # null=True, blank=True = ไม่บังคับ (สำหรับ main comment)
   # related_name='replies' = เรียก parent_comment.replies.all() ได้
   parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
   content = models.TextField()
   status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
   updated_at = models.DateTimeField(default=default_thai_time,blank=True, null=True)
   created_at  = models.DateTimeField(default=default_thai_time,blank=True, null=True)

   class Meta:
      """
      Meta class สำหรับกำหนด options เพิ่มเติม
      """
      # เรียงลำดับตาม created_at จากใหม่ไปเก่า
      ordering = ['-created_at']
      
      # สร้าง database indexes เพื่อเพิ่มความเร็วในการ query
      indexes = [
            models.Index(fields=['article', 'parent']),  # index สำหรับ filter by article และ parent
            models.Index(fields=['created_at']),         # index สำหรับ order by created_at
      ]

   def clean(self):
      """
      Custom validation method ที่จะรันก่อน save
      ป้องกันการ reply ไปยัง reply (จำกัดแค่ 2 levels)
      """
      if self.parent and self.parent.parent:
         raise ValidationError("Cannot reply to a reply. Only 2 levels allowed.")

   def __str__(self):
      return f"Comment by {self.user.username} on {self.article.title}"

