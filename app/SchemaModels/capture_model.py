from pydantic import BaseModel 
from datetime import datetime

#request body
class capture_model(BaseModel):

    api_key: str

    method: str
    useragent: str | None = None

    endpoint: str
    status_code: int
    response_time_ms: int

    request_headers: dict | None = None
    response_headers: dict | None = None

    request_body: dict | str | list | None = None
    response_body: dict | str | list | None = None

    

#response body
class capture_response(BaseModel):
    
    method : str
    endpoint : str
    status_code: int
    response_time:int
    ip_address: str
    useragent: str
    created_at : datetime


    


