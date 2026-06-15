from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.register_request import register_username 
from ..SchemaModels.register_response import registered_username
from ..services.user_service import userservices
from ..services.email_service import send_registration_otp
from ..SchemaModels.register_otp import (
    RequestOTP,
    VerifyOTP
)


router = APIRouter()


@router.post("/register/request-otp")
def request_otp(
    payload: RequestOTP,
    db: Session = Depends(get_db)
):

    check = userservices.validate_user_registration(
        payload.username,
        payload.email,
        db
    )

    if check != "username and email are available":

        raise HTTPException(
            status_code=400,
            detail=check
        )

    otp = userservices.generate_registration_otp(
        payload.email,
        db
    )

    if otp == "wait_before_requesting":

        raise HTTPException(
            status_code=429,
            detail="Please wait before requesting another OTP"
        )

    try:
    
        send_registration_otp(
            payload.email,
            otp
        )
    
    except Exception as e :
        
        print("EMAIL ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send verification email"
        )

    return {
        "message":
        "verification code sent"
    }
    

@router.post(
    "/register/verify-otp",
    response_model=registered_username
)
def verify_otp_register(
    payload: VerifyOTP,
    db: Session = Depends(get_db)
):

    result = (
        userservices.verify_registration_otp(
            payload.email,
            payload.otp,
            db
        )
    )

    if result is not True:

        raise HTTPException(
            status_code=400,
            detail=result
        )
    
    check = userservices.validate_user_registration(
        payload.username,
        payload.email,
        db
    )
    
    if check != "username and email are available":
    
        raise HTTPException(
            status_code=400,
            detail=check
        )

    reg = userservices.create_user(
        payload.username,
        payload.email,
        payload.password,
        db
    )

    api_gen = userservices.api_generation(
        reg.id,
        db
    )

    return api_gen

    
    
    