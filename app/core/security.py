from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from app.core.config import settings
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    # Use [:72] to manually truncate over 72 bytes to avoid ValueError with long passwords
    return bcrypt.checkpw(password_byte_enc[:72], hashed_password_byte_enc)

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # Use [:72] to manually truncate over 72 bytes to avoid ValueError
    hashed_password = bcrypt.hashpw(pwd_bytes[:72], salt)
    return hashed_password.decode('utf-8')

def create_access_token(subject: Union[str, Any], role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
