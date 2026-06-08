from fastapi import APIRouter , Depends , HTTPException
from ..SchemaModels.login_request import login_user , logged_user
from ..db.dependency import get_db
from sqlalchemy.orm import Session
from ..services.user_service import userservices
from ..services.jwt_service import jwt_services
router = APIRouter()

@router.post("/login" , response_model=logged_user)

def login_request(user:login_user , db: Session = Depends(get_db)) : 

    result = userservices.log_user(user.email , user.password , db)

    if not result:
        raise HTTPException(status_code=401 , detail="No Account found with that credentials")
    
    token = jwt_services.create_access_token(result.id)

    
    return {
        "access_token": token,
        "token_type": "bearer"
    } 

