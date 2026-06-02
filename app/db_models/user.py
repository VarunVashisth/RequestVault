from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String  , DateTime , func
from datetime import datetime
from app.db.database import base

class user(base) : 
   __tablename__ = "users"

   id: Mapped[int] = mapped_column(primary_key=True)
   username: Mapped[str] = mapped_column(String(255), unique=True)
   email: Mapped[str] = mapped_column(String(255), unique=True)
   password_hash: Mapped[str] = mapped_column(String(255))
   api_key: Mapped[str] = mapped_column(String(255))
   created_at: Mapped[datetime] = mapped_column(
      DateTime,
      server_default=func.now()   
   )

   
