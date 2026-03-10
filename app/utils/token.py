from datetime import datetime, timedelta
from jose import jwt
import secrets
import hashlib


SECRET_KEY = "super-secret-key-crypto"
ALGORITHM = "HS256"


def create_access_token(user_id: str):

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def generate_refresh_token():

    token = secrets.token_urlsafe(64)

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    return token, token_hash

def decode_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None