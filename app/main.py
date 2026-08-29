from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth

# Import models so SQLAlchemy knows about them before creating tables
from app.models import tenant, user

app = FastAPI(title="Business Analytics SaaS")

app.include_router(auth.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}
