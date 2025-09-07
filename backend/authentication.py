from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from user.models import User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override เพื่อใช้ User model แทน default User model
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # ใช้ User model แทน default User model
            user = User.objects.get(user_id=user_id)
            
            if not user.is_active:
                raise InvalidToken('User account is disabled')
                
            return user
        except User.DoesNotExist:
            raise InvalidToken('User not found')
        except Exception as e:
            raise InvalidToken(f'Token authentication failed: {str(e)}')