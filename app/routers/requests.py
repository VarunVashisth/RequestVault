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
    db: Session = Depends(get_db)
):
    
    user = userservices.validate_api_key(api_key, db)

    if not user:
        raise HTTPException(status_code= 401 , detail="invalid API")

    requests = analytics_service.get_requests(user.id, db)

    return requests