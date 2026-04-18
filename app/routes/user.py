from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile. Protected route.
    """
    return current_user
