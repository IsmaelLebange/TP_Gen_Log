import jwt
import datetime

class JWTProvider:
    SECRET_KEY = 'your-secret-key'

    @staticmethod
    def generate_token(payload):
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        return jwt.encode(payload, JWTProvider.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, JWTProvider.SECRET_KEY, algorithms=['HS256'])