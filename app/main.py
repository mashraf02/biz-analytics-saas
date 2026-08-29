from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, customers, products, orders

from app.models import tenant, user, customer, product, order

app = FastAPI(title="Business Analytics SaaS")

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}
