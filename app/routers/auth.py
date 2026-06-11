
from fastapi import APIRouter, Depends
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/auth/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }