from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.dependency import get_db
from ..SchemaModels.register_request import register_username
from ..SchemaModels.register_response import registered_username
from ..services.user_service import userservices

router = APIRouter()


@router.post(
    "/register",
    response_model=registered_username
)
def register(
    payload: register_username,
    db: Session = Depends(get_db)
):

    check = userservices.validate_user_registration(
        payload.username,
        db
    )

    if check != "username is available":

        raise HTTPException(
            status_code=400,
            detail=check
        )

    reg = userservices.create_user(
        payload.username,
        payload.password,
        db
    )

    api_gen = userservices.api_generation(
        reg.id,
        db
    )

    return api_gen