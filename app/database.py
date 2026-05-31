from sqlalchemy import create_engine , String , Integer , ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column




try:
  DATABASE_URL = ("postgresql+psycopg://postgres:123456789@localhost:5432/request_vault")

  engine = create_engine(DATABASE_URL)

  with engine.connect() as conn:
     print("Connection was Successfull")
except OperationalError  as err:
   print("Database Connection failed")
   print(err)

class base(DeclarativeBase):
   pass

class user(base) : 
   __tablename__ = "users"

   id: Mapped[int] = mapped_column(primary_key=True)
   email: Mapped[str] = mapped_column(String(255), unique=True)
   password_hash: Mapped[str] = mapped_column(String(255))


    
class Request(base) :
   __tablename__ = "requests"

   id: Mapped[int] = mapped_column(primary_key=True)

   user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

   endpoint: Mapped[str] = mapped_column(String(255))
   status_code: Mapped[int]