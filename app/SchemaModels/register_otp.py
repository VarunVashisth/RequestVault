
from pydantic import BaseModel, EmailStr
from .register_request import strictusername


class RequestOTP(BaseModel):
    username: strictusername
    email: EmailStr
    password: str


class VerifyOTP(BaseModel):
    username: strictusername
    email: EmailStr
    password: str
    otp: str