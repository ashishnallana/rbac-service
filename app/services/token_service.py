import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.token import RefreshToken
from app.core.config import settings

def create_refresh_token(db: Session, user_id: int) -> str:
    token_str = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        user_id=user_id,
        token=token_str,
        expires_at=expires
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return token_str

def verify_refresh_token(db: Session, token: str) -> RefreshToken:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        return None
    
    if db_token.expires_at < datetime.utcnow():
        db.delete(db_token)
        db.commit()
        return None
        
    return db_token

def revoke_refresh_token(db: Session, token: str) -> bool:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False
