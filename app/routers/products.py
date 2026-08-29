from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str
    price: Decimal
    cost: Decimal | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    price: Decimal
    cost: Decimal | None

    class Config:
        from_attributes = True


@router.post("", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = Product(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        price=payload.price,
        cost=payload.cost,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Product).filter(Product.tenant_id == current_user.tenant_id).all()
