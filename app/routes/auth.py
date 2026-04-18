from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, TokenRefreshRequest
from app.schemas.user import UserOut
from app.services.auth_service import create_user, authenticate_user, log_audit
from app.services.token_service import create_refresh_token, verify_refresh_token, revoke_refresh_token
from app.core.security import create_access_token
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    user = authenticate_user(db, user_in.email, user_in.password, ip)
    
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(request_data: TokenRefreshRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    db_token = verify_refresh_token(db, request_data.refresh_token)
    
    if not db_token:
        # Avoid user_id if we don't know it, but log attempt
        log_audit(db, None, "token_refresh", "failure", ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    # Generate new tokens
    access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token = create_refresh_token(db, user.id)
    
    # Revoke old refresh token (sliding window approach)
    revoke_refresh_token(db, request_data.refresh_token)
    
    log_audit(db, user.id, "token_refresh", "success", ip)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request_data: TokenRefreshRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ip = request.client.host
    success = revoke_refresh_token(db, request_data.refresh_token)
    if success:
        log_audit(db, current_user.id, "logout", "success", ip)
    else:
        log_audit(db, current_user.id, "logout", "failure", ip)
    return
