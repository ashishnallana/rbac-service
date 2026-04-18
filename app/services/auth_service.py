from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.redis_utils import redis_client

RATE_LIMIT_PREFIX = "login_attempts:"
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300 # 5 minutes

def log_audit(db: Session, user_id: int, action: str, status_msg: str, ip: str):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        status=status_msg,
        ip=ip
    )
    db.add(audit)
    db.commit()

def check_rate_limit(ip: str, email: str):
    key = f"{RATE_LIMIT_PREFIX}{ip}:{email}"
    attempts = redis_client.get(key)
    
    if attempts and int(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

def record_failed_attempt(ip: str, email: str):
    key = f"{RATE_LIMIT_PREFIX}{ip}:{email}"
    attempts = redis_client.get(key)
    
    if attempts:
        redis_client.incr(key)
    else:
        redis_client.setex(key, LOCKOUT_TIME, 1)

def reset_attempts(ip: str, email: str):
    key = f"{RATE_LIMIT_PREFIX}{ip}:{email}"
    redis_client.delete(key)

def create_user(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role="user" # Default role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str, ip: str) -> User:
    check_rate_limit(ip, email)
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        record_failed_attempt(ip, email)
        log_audit(db, user.id if user else None, "login", "failure", ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    reset_attempts(ip, email)
    log_audit(db, user.id, "login", "success", ip)
    return user
