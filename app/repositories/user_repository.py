from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_email(db: Session, email: str):

    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    email: str,
    username: str,
    password_hash: str
):

    user = User(
        email=email,
        username=username,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def revoke_refresh_token(db, token_hash):

    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )

    if token:
        token.revoked = True
        db.commit()

    return token

def revoke_all_user_tokens(db, user_id):

    tokens = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id)
        .all()
    )

    for token in tokens:
        token.revoked = True

    db.commit()