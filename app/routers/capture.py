from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.capture_model import capture_model
from ..SchemaModels.capture_model import capture_response
from ..services.request_service import capture_service


router = APIRouter()

@router.post("/capture" , response_model=capture_response)

def capture_request(request:capture_model  , db : Session = Depends(get_db) ) :
        
        check = capture_service.check(request.api_key , db)
        
        if not check:
                raise HTTPException(status_code=401 , detail="api_key mismatch") 
        
        result = capture_service.capture(check.id , request.endpoint , request.status_code , request.response_time_ms)
        
        return result


        
    
       


    

    
    
    