from sqlalchemy.orm import Mapped , mapped_column  
from sqlalchemy import String , ForeignKey
from db.database import base



class Request(base) :
   __tablename__ = "requests"

   id: Mapped[int] = mapped_column(primary_key=True)

   user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

   endpoint: Mapped[str] = mapped_column(String(255))
   status_code: Mapped[int]