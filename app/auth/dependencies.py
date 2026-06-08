from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.db.dependency import get_db
from ..config import SECRET_KEY, ALGORITHM
from ..db_models.user import user as User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    db_user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if db_user is None:
        raise credentials_exception

    return db_user