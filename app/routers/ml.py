from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.customer import Customer

from app.ml.forecasting import forecast_revenue
from app.ml.insights import segment_customers, detect_low_performers

router = APIRouter(prefix="/ml", tags=["ml-insights"])


@router.get("/forecast")
def get_forecast(
    days_ahead: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .filter(Order.tenant_id == current_user.tenant_id)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    history = [(row.day, row.revenue) for row in rows]
    return forecast_revenue(history, days_ahead=days_ahead)


@router.get("/customer-segments")
def get_customer_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Customer.id,
            Customer.name,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
        )
        .join(Order, Order.customer_id == Customer.id)
        .filter(Customer.tenant_id == current_user.tenant_id)
        .group_by(Customer.id, Customer.name)
        .all()
    )

    customer_data = [(row.id, row.name, row.order_count, row.total_spent) for row in rows]
    return segment_customers(customer_data)


@router.get("/low-performers")
def get_low_performers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Product.id,
            Product.name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .filter(Product.tenant_id == current_user.tenant_id)
        .group_by(Product.id, Product.name)
        .all()
    )

    product_data = [(row.id, row.name, row.quantity_sold, row.revenue) for row in rows]
    return detect_low_performers(product_data)
