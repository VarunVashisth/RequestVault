from sqlalchemy import create_engine  
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase , sessionmaker
from ..core.settings import settings

class base(DeclarativeBase):
   pass

try:
  
  print(type(settings.DATABASE_URL))

  engine = create_engine(settings.DATABASE_URL)

  with engine.connect() as conn:
     print("Connection was Successfull")
except OperationalError  as err:
   print("Database Connection failed")
   print(err)


SessionLocal = sessionmaker(
   bind = engine,
   autoflush= False,
)
