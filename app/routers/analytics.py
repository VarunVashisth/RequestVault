from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.dependency import get_db
from ..SchemaModels.analytic_model import (
    analytics_request,
    analytics_response
)
from ..services.analytic_service import analytics_service

router = APIRouter()

@router.post(
    "/analytics",
    response_model=analytics_response
)
def get_analytics(
    request: analytics_request,
    db: Session = Depends(get_db)
):

    result = analytics_service.analytics(
        request.api_key,
        db
    )

    return result