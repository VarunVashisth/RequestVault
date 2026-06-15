import random
from datetime import datetime, timedelta , timezone
from ..db_models.email_verification import RegistrationOTP
from ..db_models.user import user
from pwdlib import PasswordHash 
import secrets
from fastapi import HTTPException

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
      
      if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
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

        user_obj = (
            db.query(user)
            .filter(user.email == email)
            .first()
        )
    
        if not user_obj:
            return None
    
        if not password_hash.verify(
            password,
            user_obj.password_hash
        ):
            return None
    
        return user_obj
    
    @staticmethod
    def validate_api_key(api : str , db) :

        val_api = (
            db.query(user)
            .filter(user.api_key == api)
            .first()
        )
       
 
          
        return val_api

    @staticmethod
    def generate_registration_otp(
        email: str,
        db
    ):
    
        existing = (
            db.query(RegistrationOTP)
            .filter(
                RegistrationOTP.email == email
            )
            .first()
        )

        if existing:

            if existing.expires_at > datetime.now(timezone.utc):
        
                return "wait_before_requesting"
    
            else:
    
                db.delete(existing)
                db.commit()
    
        otp = str(
            random.randint(
                100000,
                999999
            )
        )
    
        record = RegistrationOTP(
            email=email,
            otp=otp,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
    
        db.add(record)
        db.commit()
    
        return otp
    
    
    @staticmethod
    def verify_registration_otp(
        email: str,
        otp: str,
        db
    ):
    
        record = (
            db.query(RegistrationOTP)
            .filter(
                RegistrationOTP.email == email
            )
            .first()
        )
    
        if not record:
            return "otp not found"
    
        if record.expires_at < datetime.now(timezone.utc):
            return "otp expired"
    
        if record.attempts >= 5:
            db.delete(record)
            db.commit()
            return "too many attempts"
    
        if record.otp != otp:
    
            record.attempts += 1
    
            db.commit()
    
            return "invalid otp"
    
        db.delete(record)
        db.commit()
    
        return True