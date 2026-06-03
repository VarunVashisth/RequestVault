from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String  , DateTime , func , Integer
from datetime import datetime
from app.db.database import base
from typing import Optional

class user(base) : 
   __tablename__ = "users"

   id: Mapped[int] = mapped_column(Integer , primary_key=True)
   username: Mapped[str] = mapped_column(String(255), unique=True)
   email: Mapped[str] = mapped_column(String(255), unique=True)
   password_hash: Mapped[str] = mapped_column(String(255))
   api_key: Mapped[Optional[str]] = mapped_column(String(255) , nullable=True , unique = True)
   created_at: Mapped[datetime] = mapped_column(
      DateTime,
      server_default=func.now()   
   )

   
