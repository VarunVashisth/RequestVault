from pydantic import BaseModel , EmailStr , StringConstraints
from typing import Annotated

strictusername = Annotated[
    str ,
    StringConstraints(
        strip_whitespace= True,
        pattern=r"^[a-z0-9_-]+$" ,
        min_length= 5,
        max_length=20
    ) 
] 

class register_username(BaseModel):
    username : strictusername 
    email : EmailStr
    password : str




