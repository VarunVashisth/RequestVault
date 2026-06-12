from fastapi import APIRouter , Depends , HTTPException , Request
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.capture_model import capture_model
from ..SchemaModels.capture_model import capture_response
from ..services.request_service import capture_service , sanitize_body


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
        
        useragent = request.headers.get("user-agent")
        method = request.method
        request_body = sanitize_body(request_data.request_body)
        response_body = sanitize_body(request_data.response_body)
        request_headers = capture_service.sanitize_headers(request_data.request_headers)
        response_headers = capture_service.sanitize_headers(request_data.response_headers)
        request_body = capture_service.limit_size(request_body)
        response_body = capture_service.limit_size(response_body)
        request_headers = capture_service.limit_size(request_headers)
        response_headers = capture_service.limit_size(response_headers)
        result = capture_service.capture(
 
            check.id,
            request_data.endpoint,
            request_data.status_code,
            request_data.response_time_ms,
            ip,
            useragent,
            method,    
            request_body,
            response_body,
    
            request_headers,
            response_headers,
    
            db
        )        
        return result


        
    
       


    

    
    
    