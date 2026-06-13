from fastapi import APIRouter , Depends , HTTPException , Request
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.capture_model import capture_model
from ..SchemaModels.capture_model import capture_response
from ..services.request_service import capture_service , sanitize_body


router = APIRouter()

@router.post("/capture" , response_model=capture_response)

def capture_request(
    request_data: capture_model,
    request: Request,
    db: Session = Depends(get_db)
):

    user = capture_service.check(
        request_data.api_key,
        db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="api_key mismatch"
        )

    forwarded_for = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = (
            request.client.host
            if request.client
            else "Unknown"
        )

    request_body = sanitize_body(
        request_data.request_body
    )

    response_body = sanitize_body(
        request_data.response_body
    )

    request_headers = (
        capture_service.sanitize_headers(
            request_data.request_headers
        )
    )

    response_headers = (
        capture_service.sanitize_headers(
            request_data.response_headers
        )
    )

    request_body = capture_service.limit_size(
        request_body
    )

    response_body = capture_service.limit_size(
        response_body
    )

    request_headers = capture_service.limit_size(
        request_headers
    )

    response_headers = capture_service.limit_size(
        response_headers
    )

    result = capture_service.capture(

        user.id,

        request_data.endpoint,
        request_data.status_code,
        request_data.response_time_ms,

        ip,

        request_data.useragent,
        request_data.method,

        request_body,
        response_body,

        request_headers,
        response_headers,

        db
    )

    return result

        
    
       


    

    
    
    