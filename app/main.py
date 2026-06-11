from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.db.init_db import init_db
from app.routers import register , login , capture ,analytics , requests , auth
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(capture.router)
app.include_router(analytics.router)
app.include_router(requests.router)
app.include_router(auth.router)


@app.on_event("startup")

def startup():
    init_db()

