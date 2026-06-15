import random
from datetime import datetime, timedelta , timezone
from ..db_models.user import user
from pwdlib import PasswordHash 
import secrets
from fastapi import HTTPException

password_hash = PasswordHash.recommended()

class userservices():
    
    @staticmethod
    def validate_user_registration(
        username: str,
        db
    ):
    
        existing_username = (
            db.query(user)
            .filter(user.username == username)
            .first()
        )
    
        if existing_username:
            return "username already exists"
    
        return "username is available" 
    
    @staticmethod
    def create_user(
        user_name: str,
        password: str,
        db
    ):
    
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters"
            )
    
        pass_hash = password_hash.hash(password)
    
        new_user = user(
            username=user_name,
            email=None,
            password_hash=pass_hash
        )
    
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
    def log_user(username:str , password:str , db):

        user_obj = (
            db.query(user)
            .filter(user.username == username)
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

 