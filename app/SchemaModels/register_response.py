from pydantic import BaseModel , EmailStr , StringConstraints
from typing import Annotated



class registered_username(BaseModel):
    username : str 
    email : EmailStr 
    api_key: str
    




