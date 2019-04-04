import jwt
from django.conf import settings
from datetime import datetime, timedelta


def jwt_encode(user_id=None, days=None):
    if user_id:
        if days:
            duration = datetime.now() + timedelta(days)
            token = jwt.encode(
                {
                    "user_id": user_id,
                    "exp": int(duration.strftime('%s'))
                }, 
                settings.SECRET_KEY,
                algorithm='HS256')
        else:
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
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms='HS256'
        )
        return payload
    else:
        return None
