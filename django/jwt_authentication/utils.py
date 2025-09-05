import jwt
from datetime import datetime, timedelta
from django.conf import settings

class JWTUtils:
    @staticmethod
    def generate_tokens(sub_obj):
        payload = {
                "sub": str(sub_obj.id),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 30)),
        }

        additional_payload = {}
        for sub_attr in getattr(settings, 'JWT_SUBJECT_ATTRIBUTES_AS_ADDITIONAL_CLAIMS', []):
            additional_payload = additional_payload | {sub_attr: getattr(sub_obj, sub_attr, None)}

        payload = payload | additional_payload
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return access_token

    @staticmethod
    def validate_token(token):
        try:
            payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
