from pydantic import BaseModel 

#request body
class capture_model(BaseModel):
    api_key : str
    endpoint : str
    status_code: int
    response_time_ms:int

#response body
class capture_response(BaseModel):
    
    endpoint : str
    status_code: int
    response_time_ms:int
    captured_at : int


    


