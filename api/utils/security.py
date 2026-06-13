import hashlib
from jose import jwt, JWTError

SECRET_KEY = "ebm-secret-key-change-in-production"
ALGORITHM  = "HS256"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_token(user_id: int) -> str:
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["user_id"]
