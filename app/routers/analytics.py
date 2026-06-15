from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from  ..auth.dependencies import get_current_user
from ..db.dependency import get_db
from ..SchemaModels.analytic_model import  analytics_response

from ..services.analytic_service import analytics_service

router = APIRouter()

@router.get(
    "/analytics",
    response_model=analytics_response
)
def get_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    result = analytics_service.analytics(
        current_user.id,
        db
    )

    return result

@router.get("/analytics/status-distribution")
def get_status_distribution(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.status_distribution(
        current_user.id,
        db
    )


@router.get("/analytics/top-endpoints" , response_model=analytics_response)
def get_top_endpoints(
    limit: int = 5,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.top_endpoints(
        current_user.id,
        limit,
        db
    )


@router.get("/analytics/response-times")
def get_response_times(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.response_times(
        current_user.id,
        db
    )


@router.get("/analytics/request-volume")
def get_request_volume(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.request_volume(
        current_user.id,
        db
    )


@router.get("/analytics/recent" , response_model=analytics_response)
def get_recent_requests(
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.recent_requests(
        current_user.id,
        limit,
        db
    )


@router.get("/analytics/errors")
def get_errors(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.errors(
        current_user.id,
        db
    )


@router.get("/analytics/slow-endpoints" , response_model=analytics_response)
def get_slow_endpoints(
    limit: int = 5,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return analytics_service.slow_endpoints(
        current_user.id,
        limit,
        db
    )