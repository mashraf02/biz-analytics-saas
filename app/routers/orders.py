from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int | None = None
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    customer_id: int | None
    total_amount: Decimal
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    order = Order(tenant_id=current_user.tenant_id, customer_id=payload.customer_id, total_amount=0)
    db.add(order)
    db.flush()  # get order.id before committing

    total = Decimal("0")

    for item in payload.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id, Product.tenant_id == current_user.tenant_id)
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if item.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")

        line_total = product.price * item.quantity
        total += line_total

        order_item = OrderItem(
            tenant_id=current_user.tenant_id,
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
        )
        db.add(order_item)

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Order).filter(Order.tenant_id == current_user.tenant_id).all()
