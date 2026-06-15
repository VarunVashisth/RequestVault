from pydantic import BaseModel  , StringConstraints
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
    username : str
    password : str
    

#response body
class logged_user(BaseModel):
    access_token : str
    token_type: str
    
    


