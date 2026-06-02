from ..db_models.user import user
from sqlalchemy.orm import query 

class userservices():

    def validate_username(username:str , email:str, db) :
          
        existing_username = (
            db.query(user).filter(user.username == username).first()
        )

        if existing_username : 
            return "username already exists"
        
        existing_email = (
            db.query(user).filter(user.email == email).first()
        )

        if existing_email :
            return("another account uses this email")
        
        return("username and email are available")        
    