from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


def create_refresh_token(db: Session, token: RefreshToken):

    db.add(token)
    db.commit()
    db.refresh(token)

    return token

def get_refresh_token_by_hash(db: Session, token_hash: str):

    return (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )