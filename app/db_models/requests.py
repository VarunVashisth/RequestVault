from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String , ForeignKey , DateTime , func , JSON , Text
from datetime import datetime
from app.db.database import base



class Request(base) :
   __tablename__ = "requests"

   id: Mapped[int] = mapped_column(primary_key=True)

   user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
   ip_address: Mapped[str] = mapped_column(String(255))
   method : Mapped[str] = mapped_column(String(20))
   useragent : Mapped[str] = mapped_column(Text)
   endpoint: Mapped[str] = mapped_column(Text)
   status_code: Mapped[int]
   response_time : Mapped[int]
   request_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   response_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   request_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   response_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
   created_at: Mapped[datetime] = mapped_column(
      DateTime(timezone=True),
      server_default=func.now() 
   )