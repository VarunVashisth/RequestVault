from fastapi import APIRouter , Depends , HTTPException , Request
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.capture_model import capture_model
from ..SchemaModels.capture_model import capture_response
from ..services.request_service import capture_service


router = APIRouter()

@router.post("/capture" , response_model=capture_response)

def capture_request(request_data:capture_model , request: Request , db : Session = Depends(get_db) ) :
        
        check = capture_service.check(request_data.api_key , db)
        forwaded_for = request.headers.get("x-forwarded-for")
        if forwaded_for:
            ip = forwaded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "Unknown"

        if not check:
                raise HTTPException(status_code=401 , detail="api_key mismatch") 
        useragnet = request.headers.get("user-agent")
        method = request.method
        
        result = capture_service.capture(check.id , request_data.endpoint , request_data.status_code , request_data.response_time_ms, ip ,useragnet , method , db)
        
        return result


        
    
       


    

    
    
    