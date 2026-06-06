from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.request_response import RequestResponse
from ..services.user_service import userservices
from ..services.analytic_service import analytics_service

router = APIRouter()

@router.get("/requests", response_model=list[RequestResponse])
def get_requests(
    api_key: str,
    search : str | None=None,
    status_code : int | None=None,
    cursor: int | None=None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    
    user = userservices.validate_api_key(api_key, db)

    if not user:
        raise HTTPException(status_code= 401 , detail="invalid API")

    requests = analytics_service.get_requests(user.id , search , status_code ,cursor , limit , db)

    return requests


@router.delete("/requests/{request_id}")
def delete_request(
    request_id: int,
    api_key: str,
    db: Session = Depends(get_db)
):

    user = userservices.validate_api_key(api_key, db)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    result = analytics_service.delete_request(
        request_id,
        user.id,
        db
    )

    return result