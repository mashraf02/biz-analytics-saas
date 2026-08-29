from typing import List
from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product


def to_decimal(value) -> Decimal:
    """Safely convert any numeric value from the DB into a clean Decimal."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


router = APIRouter(prefix="/analytics", tags=["analytics"])


class SummaryOut(BaseModel):
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal


class BestProductOut(BaseModel):
    product_id: int
    name: str
    quantity_sold: int
    revenue: Decimal


class RevenuePointOut(BaseModel):
    day: date
    revenue: Decimal


@router.get("/summary", response_model=SummaryOut)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = (
        db.query(
            func.sum(Order.total_amount).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
        )
        .filter(Order.tenant_id == current_user.tenant_id)
        .first()
    )

    total_revenue = to_decimal(result.total_revenue)
    total_orders = result.total_orders or 0

    if total_orders > 0:
        average_order_value = (total_revenue / total_orders).quantize(Decimal("0.01"))
    else:
        average_order_value = Decimal("0.00")

    return SummaryOut(
        total_revenue=total_revenue,
        total_orders=total_orders,
        average_order_value=average_order_value,
    )


@router.get("/best-products", response_model=List[BestProductOut])
def get_best_products(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("name"),
            func.sum(OrderItem.quantity).label("quantity_sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .filter(Product.tenant_id == current_user.tenant_id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
        .limit(limit)
        .all()
    )

    return [
        BestProductOut(
            product_id=row.product_id,
            name=row.name,
            quantity_sold=row.quantity_sold or 0,
            revenue=to_decimal(row.revenue),
        )
        for row in rows
    ]


@router.get("/revenue-trend", response_model=List[RevenuePointOut])
def get_revenue_trend(
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

    return [RevenuePointOut(day=row.day, revenue=to_decimal(row.revenue)) for row in rows]
