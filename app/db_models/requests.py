from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String , ForeignKey , DateTime , func
from datetime import datetime
from app.db.database import base



class Request(base) :
   __tablename__ = "requests"

   id: Mapped[int] = mapped_column(primary_key=True)

   user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
   
   endpoint: Mapped[str] = mapped_column(String(255))
   status_code: Mapped[int]
   response_time : Mapped[int]
   created_at: Mapped[datetime] = mapped_column(
      DateTime(timezone=True),
      server_default=func.now() 
   )