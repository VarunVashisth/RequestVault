from ..db_models.user import user
from sqlalchemy.orm import query 
from pwdlib import PasswordHash
import secrets

password_hash = PasswordHash.recommended()

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
    

    def create_user(user_name:str , _email_:str , password:str , db) :
      
      pass_hash = password_hash.hash(password)
      try:
        new_user = user(username = user_name , email = _email_ , password_hash = pass_hash)
        db.add(new_user)
        db.commit()

        user_id = new_user.id
        return user_id
      
      finally:

        db.close()

        
    
    def api_generation(id:int , user_name:str , _email_:str , password:str , db):

            

         
        pass
    
    
    