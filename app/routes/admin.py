from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.models.user import User
from app.core.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/data")
def get_admin_data(current_admin: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """
    Get sensitive admin data. Protected route, RBAC requires 'admin' role.
    """
    return {
        "message": f"Welcome Admin {current_admin.email}",
        "sensitive_data": "This is protected data only visible to administrators."
    }
