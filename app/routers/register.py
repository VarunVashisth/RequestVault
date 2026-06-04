from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.register_request import register_username 
from ..SchemaModels.register_response import registered_username
from ..services.user_service import userservices

router = APIRouter()

@router.post("/register" , response_model=registered_username)

def create_user(user:register_username , db : Session = Depends(get_db) ) :

    check = userservices.validate_user_registration(user.username , user.email , db)
    
    if check=="username and email are available" :
        reg = userservices.create_user(user.username,user.email,user.password,db)
    else:
        raise HTTPException(status_code=400 , detail=check)
    
    if reg:
        api_gen = userservices.api_generation(reg.id , db)
    else:
        raise HTTPException( status_code=500 , detail="User Creation Failed")    
    
    return api_gen

    



    

    
    
    