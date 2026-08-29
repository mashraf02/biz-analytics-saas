from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, customers, products, orders, analytics, integrations, ml

from app.models import tenant, user, customer, product, order, integration

app = FastAPI(title="Business Analytics SaaS")

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(integrations.router)
app.include_router(ml.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}
