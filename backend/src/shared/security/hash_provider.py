import hashlib

class HashProvider:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()