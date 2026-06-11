from pydantic import BaseModel 
from datetime import datetime

#request body
class capture_model(BaseModel):
    api_key : str
    endpoint : str
    status_code: int
    response_time_ms:int
    

#response body
class capture_response(BaseModel):
    
    method : str
    endpoint : str
    status_code: int
    response_time:int
    ip_address: str
    useragent: str
    created_at : datetime


    


