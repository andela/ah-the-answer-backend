import jwt
from django.conf import settings


def jwt_encode(user_id=None):
    if user_id:
        token = jwt.encode(
            {
                "user_id": user_id
            },
            settings.SECRET_KEY,
            algorithm='HS256'
        )

        return token.decode('utf-8')
    else:
        return None


def jwt_decode(token=None):
    if token:
        jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
    else:
        return None
