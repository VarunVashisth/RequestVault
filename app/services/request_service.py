from ..db_models.user import user
from ..db_models.requests import Request
import json

MAX_BODY_SIZE = 10000

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key"
}

SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "secret"
}

def sanitize_body(data):
        if data is None:
            return None
    
        if isinstance(data, dict):
            cleaned = {}
    
            for key, value in data.items():
    
                if key.lower() in SENSITIVE_FIELDS:
                    cleaned[key] = "[REDACTED]"
    
                elif isinstance(value, (dict, list)):
                    cleaned[key] = sanitize_body(value)
    
                else:
                    cleaned[key] = value
    
            return cleaned
    
        if isinstance(data, list):
            return [sanitize_body(item) for item in data]
    
        return data
    

class capture_service():

    @staticmethod
    def check(api:str, db) :
    
    
        check_user =  (
            db.query(user).filter(user.api_key == api).first()
        )

        return check_user
    
    @staticmethod
    def capture(id:int , endpoint:str , status_code:int , response_time: int , ip:str , user_agent:str ,  method:str ,request_body,response_body,request_headers ,response_headers, db):


        capture = Request(user_id = id ,ip_address =ip, method = method , endpoint = endpoint , status_code = status_code , useragent = user_agent, response_time = response_time , request_body = request_body , response_body=response_body , request_headers=request_headers , response_headers=response_headers)

        db.add(capture)
        db.commit()
        db.refresh(capture)

        return capture
    
    @staticmethod
    def sanitize_headers(headers: dict | None):
        if not headers:
            return None
    
        cleaned = {}
    
        for key, value in headers.items():
            if key.lower() in SENSITIVE_HEADERS:
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = value
    
        return cleaned
    
    

    @staticmethod
    def limit_size(data):
        if data is None:
            return None
    
        text = json.dumps(data)
    
        if len(text) > MAX_BODY_SIZE:
            return {
                "truncated": True,
                "preview": text[:MAX_BODY_SIZE]
            }
    
        return data

        


