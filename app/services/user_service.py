from ..db_models.user import user
from pwdlib import PasswordHash 
import secrets

password_hash = PasswordHash.recommended()

class userservices():
    
    @staticmethod
    def validate_user_registration(username:str , email:str, db) :
          
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
    
    @staticmethod
    def create_user(user_name:str , _email_:str , password:str , db) :
      
      pass_hash = password_hash.hash(password)
      
      new_user = user(username = user_name , email = _email_ , password_hash = pass_hash)
      db.add(new_user)
      db.commit()  
      db.refresh(new_user)
      return new_user
      
      

        
    @staticmethod
    def api_generation(id:int , db):

        api_key = f"rv_{secrets.token_urlsafe(32)}"

        update_user = db.get(user , id)

        if update_user:
           update_user.api_key = api_key
           db.commit()
           db.refresh(update_user)
        else:
           return("There has been some problem...")

         
        return update_user
    
    @staticmethod
    def log_user(email:str , password:str , db):

        log_user = (
            db.query(user).filter(user.email == email ).first()
        )

        if not log_user:
         return("user not found")

        try:
            password_hash.verify(password, log_user.password_hash)
        except Exception :
           return("invalid password")
           
        
        return log_user
    
    @staticmethod
    def validate_api_key(api : str , db) :
       
       val_api = (
          db.query(user).filter(user.api_key == api).first()
       )

       return val_api


    
    
    