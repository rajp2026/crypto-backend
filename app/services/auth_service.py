import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    get_user_by_email,
    create_user
)

from app.utils.password import hash_password

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.repositories.user_repository import get_user_by_email
from app.repositories.token_repository import create_refresh_token

from app.utils.password import verify_password
from app.utils.token import create_access_token, generate_refresh_token

from app.models.refresh_token import RefreshToken


import hashlib
from datetime import datetime

from app.repositories.token_repository import get_refresh_token_by_hash
from app.utils.token import create_access_token




def register_user(
    db: Session,
    email: str,
    username: str,
    password: str
):

    existing_user = get_user_by_email(db, email)

    if existing_user:
        raise ValueError("User already exists")

    password_hash = hash_password(password)

    user = create_user(
        db=db,
        email=email,
        username=username,
        password_hash=password_hash
    )

    return user

def login_user(
    db: Session,
    email: str,
    password: str,
    device: str = "unknown"
):

    user = get_user_by_email(db, email)

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    # Create access token
    access_token = create_access_token(str(user.id))

    # Create refresh token
    refresh_token, token_hash = generate_refresh_token()

    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        device=device,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    create_refresh_token(db, refresh_token_obj)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def refresh_access_token(
    db: Session,
    refresh_token: str
):

    # hash incoming token
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    token = get_refresh_token_by_hash(db, token_hash)

    if not token:
        raise ValueError("Invalid refresh token")

    if token.revoked:
        raise ValueError("Token revoked")

    if token.expires_at < datetime.now(timezone.utc):
        raise ValueError("Refresh token expired")

    access_token = create_access_token(str(token.user_id))

    return {
        "access_token": access_token
    }


def logout_user(db, refresh_token: str):

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    revoke_refresh_token(db, token_hash)


def logout_all_devices(db, user_id):

    revoke_all_user_tokens(db, user_id)


def forgot_password(db, email):

    user = get_user_by_email(db, email)

    if not user:
        return

    token = secrets.token_urlsafe(32)

    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)

    db.commit()

    return token



def reset_password(db, token, new_password):

    user = (
        db.query(User)
        .filter(User.reset_token == token)
        .first()
    )

    if not user:
        raise ValueError("Invalid token")

    if user.reset_token_expiry < datetime.utcnow():
        raise ValueError("Token expired")

    user.password_hash = hash_password(new_password)

    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()