from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String 
from db.database import base

class user(base) : 
   __tablename__ = "users"

   id: Mapped[int] = mapped_column(primary_key=True)
   email: Mapped[str] = mapped_column(String(255), unique=True)
   password_hash: Mapped[str] = mapped_column(String(255))
   api_key: Mapped[str] = mapped_column(String(255))

   
