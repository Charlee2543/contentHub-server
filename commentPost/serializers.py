from rest_framework import serializers
from .models import Comment

class UserSerializer(serializers.Serializer):
   """
   Serializer สำหรับ User data (read-only)
   ไม่ใช้ ModelSerializer เพราะต้องการแค่ field บางตัว
   """
   user_id = serializers.CharField(source="user.user_id", read_only=True)
   username = serializers.CharField(source="user.username", read_only=True)
   picture = serializers.CharField(source="user.profile_picture_url", read_only=True)


class CommentSerializer(serializers.ModelSerializer):
   """
   Main Serializer สำหรับแสดงข้อมูล Comment (สำหรับ GET requests)
   """
   user = UserSerializer(read_only=True)
   # SerializerMethodField = field ที่คำนวณจาก method
   replies_count = serializers.SerializerMethodField()
   replies = serializers.SerializerMethodField()
   
   user_id = serializers.CharField(source="user.user_id", read_only=True)
   username = serializers.CharField(source="user.username", read_only=True)
   picture = serializers.CharField(source="user.profile_picture_url", read_only=True)
   class Meta:
      model = Comment
      fields = '__all__'
      # ['id',"replies_count","replies","content","status","updated_at","created_at","article","parent"]
      # fields ที่ไม่ให้แก้ไข
      extra_fields=['user_id','username','picture']
      # read_only_fields = ['user', 'created_at', 'updated_at']

   def get_replies_count(self, obj):
      """
      Method สำหรับ replies_count field
      นับจำนวน replies ที่ active
      """
      return obj.replies.filter(status='active').count()

   def get_replies(self, obj):
      """
      Method สำหรับ replies field
      ส่งเฉพาะ reply level 1 เท่านั้น (ป้องกัน infinite recursion)
      """
      if obj.parent is None:  # ถ้าเป็น main comment
            replies = obj.replies.filter(status='active').order_by('created_at')
            # เรียก serializer ตัวเองแบบ recursive
            return CommentSerializer(replies, many=True, context=self.context).data
      return []
class CommentCreateSerializer(serializers.ModelSerializer):
   """
   Serializer สำหรับสร้าง Comment ใหม่ (สำหรับ POST requests)
   แยกจาก CommentSerializer เพื่อให้ควบคุม validation ได้ดีกว่า
   """
   class Meta:
      model = Comment
      fields = ['article', 'parent', 'content',"user"]

   def validate_parent(self, value):
      """
      Custom validation สำหรับ parent field
      ตรวจสอบว่าไม่ใช่การ reply ต่อ reply
      """
      
      # เพิ่ม เช็ครับ article_id user_id มาด้วย
      if value and value.parent:
            raise serializers.ValidationError("Cannot reply to a reply.")
      return value

   def create(self, validated_data):
      """
      Override create method เพื่อเพิ่ม user จาก request
      """
      validated_data['user'] = self.context['request'].user
      return super().create(validated_data)