from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.request_response import RequestResponse
from ..services.user_service import userservices
from ..services.analytic_service import analytics_service
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/api-keys")
def get_api_key(
    current_user = Depends(get_current_user)
):
    
    return {
        "api_key": current_user.api_key,
        "created_at": current_user.created_at
    }


@router.post("/api-keys/regeneration")
def regenerate_api_key(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
      api_key = userservices.api_generation(current_user.id , db)

      return {
           "api_key": api_key.api_key,
           "created_at": current_user.created_at
      }
