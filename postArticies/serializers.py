from rest_framework import serializers
from .models import Articles

#ใช้ Django REST Framework แปลงข้อมูล model เป็น JSON response
class PostSerializer(serializers.ModelSerializer):
    # serializers.ModelSerializer จะจัดการ create update ให้เองโดยกำหนด class Meta
    author_username = serializers.CharField(source="author.username", read_only=True)

    # author_username = serializers.SerializerMethodField()
    # author_email = serializers.SerializerMethodField()    
    class Meta:
        model = Articles
        fields = '__all__'
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
            'picture': {'required': False, 'allow_blank': True},
            'content': {'required': False, 'allow_blank': True},
            'author': {'required': False},
        }
        extra_fields = ["author_username"]
        # required=False:ไม่จำเป็นต้องมีค่าอยู่ในอินพุต และจะไม่ถูกส่งต่อ.create()หรือ.update()ถ้าไม่เห็น
        # allow_blank=True: ''เป็นอินพุตที่ถูกต้อง สำหรับCharFieldและซับคลาสเท่านั้น
                

    def validate_title(self, value):
        print("validate title")
        print(value)
        if not value:
            raise serializers.ValidationError("title ต้องใส่")
        return value

    def validate_picture(self, value):
        print("validate picture")
        print(value)
        if not value:
            raise serializers.ValidationError("non picture")
        return value

    def validate_content(self, value):
        print("validate content")
        if not value:
            raise serializers.ValidationError("content ต้องใส่")
        return value

    def validate_author(self, value):
        print("validate author")
        if not value:
            raise serializers.ValidationError("author ต้องใส่")
        return value