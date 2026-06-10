import bcrypt

class SecurityPasswordUtil:
    @staticmethod
    def hash_password(password: str) -> str:
        byte_pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(byte_pwd, salt)
        return hashed_pwd.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        byte_pwd = plain_password.encode('utf-8')
        byte_hashed = hashed_password.encode('utf-8')
        return bcrypt.checkpw(byte_pwd, byte_hashed)