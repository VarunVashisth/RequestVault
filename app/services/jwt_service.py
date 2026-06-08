from datetime import datetime , timedelta , timezone
from jose import jwt , JWTError
from ..config import SECRET_KEY , ALGORITHM , ACCESS_TOKEN_EXPIRE_MINUTES

class jwt_services():

    @staticmethod
    def create_access_token(user_id: int ):
    
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
        payload = {
            "sub": str(user_id),
            "exp": expire
        }
    
    
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )