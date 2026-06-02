from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.register_request import register_username 
from ..services.user_service import userservices

router = APIRouter()

@router.post("/register")

def create_user(user:register_username , db : Session = Depends(get_db) ) :

    result = userservices.validate_username(user.username , user.email , db)

    

    return { 
        "result": result
    }
    
    