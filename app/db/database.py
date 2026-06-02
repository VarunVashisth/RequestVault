from sqlalchemy import create_engine  
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase , sessionmaker


class base(DeclarativeBase):
   pass

try:
  DATABASE_URL = ("postgresql+psycopg://postgres:123456789@localhost:5432/request_vault")

  engine = create_engine(DATABASE_URL)

  with engine.connect() as conn:
     print("Connection was Successfull")
except OperationalError  as err:
   print("Database Connection failed")
   print(err)


SessionLocal = sessionmaker(
   bind = engine,
   autoflush= False,
)
