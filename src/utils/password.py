import bcrypt


def generate_password_hash(password:str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def check_password_hash(password:str, hashed_password: bytes):
    bcrypt.checkpw(password.encode(), hashed_password)
