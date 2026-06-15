from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.request_response import RequestResponse , AnalyticResponse
from ..services.user_service import userservices
from ..services.analytic_service import analytics_service
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/requests", response_model=list[AnalyticResponse])
def get_requests(
    current_user=Depends(get_current_user),
    search : str | None=None,
    status_code : int | None=None,
    method: str | None = None,
    sort : str = "desc",
    cursor: int | None=None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    


    requests = analytics_service.get_requests(current_user.id , search , status_code,method,sort,cursor , limit , db)

    return requests

@router.get(
    "/requests/{request_id}",
    response_model=RequestResponse
)
def get_request_by_id(
    request_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    request = analytics_service.get_request_by_id(
        request_id,
        current_user.id,
        db
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return request

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

@router.delete("/requests/bulk")
def delete_all_requests(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    result = analytics_service.delete_all_requests(
        current_user.id,
        db
    )

    return result

@router.delete("/requests/failed")
def delete_failed_requests(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.delete_failed_requests(
        current_user.id,
        db
    )