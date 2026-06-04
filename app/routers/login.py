from fastapi import APIRouter , Depends
from ..SchemaModels.login_request import login_user , logged_user
from ..db.dependency import get_db
from sqlalchemy.orm import Session
from ..services.user_service import userservices

router = APIRouter()

@router.post("/login" , response_model=logged_user)

def login_request(user:login_user , db: Session = Depends(get_db)) : 

    result = userservices.log_user(user.email , user.password , db)

    return result