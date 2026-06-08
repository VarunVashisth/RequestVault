from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.request_response import RequestResponse
from ..services.user_service import userservices
from ..services.analytic_service import analytics_service
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/requests", response_model=list[RequestResponse])
def get_requests(
    current_user=Depends(get_current_user),
    search : str | None=None,
    status_code : int | None=None,
    cursor: int | None=None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    


    requests = analytics_service.get_requests(current_user.id , search , status_code ,cursor , limit , db)

    return requests


@router.delete("/requests/{request_id}")
def delete_request(
    request_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):



    result = analytics_service.delete_request(
        request_id,
        current_user.id,
        db
    )

    return result