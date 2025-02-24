import bcrypt


class Hash:
    @staticmethod
    def encrypt(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
