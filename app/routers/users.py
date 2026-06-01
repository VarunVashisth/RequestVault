from fastapi import APIRouter


router = APIRouter()

@router.POST("/users")

def create_user(username:str , email:str) :
    