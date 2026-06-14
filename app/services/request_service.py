from ..db_models.user import user
from ..db_models.requests import Request
import json 
from decimal import Decimal
from datetime import date, datetime

MAX_BODY_SIZE = 10000

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "secret",
    "api-key",
    "apikey",
    "auth",
    "jwt",
}

SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "auth",
    "credential",
    "jwt",
    "cookie",
    "api_key",
    "private_key",
    "secret_key",
}

def sanitize_body(data):

    if data is None:
        return None

    if isinstance(data, (bytes, bytearray)):

        try:
            decoded = data.decode("utf-8")

            try:
                return sanitize_body(
                    json.loads(decoded)
                )

            except Exception:
                return decoded

        except Exception:
            return "[BINARY_DATA]"

    if isinstance(data, (datetime, date)):
        return data.isoformat()

    if isinstance(data, Decimal):
        return float(data)

    if isinstance(data, dict):

        cleaned = {}

        for key, value in data.items():

            key_str = str(key)
            lower_key = key_str.lower()

            if any(
                pattern in lower_key
                for pattern in SENSITIVE_FIELDS
            ):
                cleaned[key_str] = "[REDACTED]"

            else:
                cleaned[key_str] = sanitize_body(value)

        return cleaned

    if isinstance(data, list):
        return [sanitize_body(item) for item in data]

    if isinstance(data, tuple):
        return [sanitize_body(item) for item in data]

    if isinstance(data, set):
        return [sanitize_body(item) for item in data]

    if isinstance(data, str):

        stripped = data.strip()

        if (
            stripped.startswith("{")
            or stripped.startswith("[")
        ):
            try:
                parsed = json.loads(data)

                return sanitize_body(parsed)

            except Exception:
                pass

        return data

    if isinstance(data, (bool, int, float)):
        return data

    try:
        return str(data)

    except Exception:
        return "[UNSERIALIZABLE_OBJECT]"

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
    def sanitize_headers(headers):

        if not headers:
            return None
    
        cleaned = {}
    
        for key, value in headers.items():
    
            key_str = str(key)
            lower_key = key_str.lower()
    
            if any(
                pattern in lower_key
                for pattern in SENSITIVE_HEADERS
            ):
                cleaned[key_str] = "[REDACTED]"
                continue
    
            if value is None:
                cleaned[key_str] = None
    
            elif isinstance(
                value,
                (bool, int, float, str)
            ):
                cleaned[key_str] = value
    
            elif isinstance(
                value,
                (bytes, bytearray)
            ):
                try:
                    decoded = value.decode("utf-8")
    
                    try:
                        cleaned[key_str] = json.loads(decoded)
        
                    except Exception:
                        cleaned[key_str] = decoded
    
                except Exception:
                    cleaned[key_str] = "[BINARY_DATA]"
    
            else:
                try:
                    cleaned[key_str] = repr(value)
                except Exception:
                    cleaned[key_str] = "[UNSERIALIZABLE_HEADER]"
    
        return cleaned
    
    

    @staticmethod
    def limit_size(data):
        if data is None:
            return None
    
        try:
            text = json.dumps(
                data,
                default=str,
                ensure_ascii=False
            )
    
        except Exception:
            text = str(data)
    
        if len(text) <= MAX_BODY_SIZE:
            return data
    
        return {
            "truncated": True,
            "original_size": len(text),
            "preview_size": MAX_BODY_SIZE,
            "preview": text[:MAX_BODY_SIZE]
        }

        


