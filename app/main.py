from fastapi import FastAPI
from app.db.init_db import init_db
from app.routers import register , login , capture ,analytics , requests
app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(capture.router)
app.include_router(analytics.router)
app.include_router(requests.router)



@app.on_event("startup")

def startup():
    init_db()

