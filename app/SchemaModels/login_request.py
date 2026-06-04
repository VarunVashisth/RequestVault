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

#request body
class login_user(BaseModel):
    email : EmailStr
    password : str
    

#response body
class logged_user(BaseModel):
    username : str
    email : EmailStr
    
    


