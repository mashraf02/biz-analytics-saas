import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem

router = APIRouter(prefix="/exports", tags=["exports"])


def csv_response(rows: list[dict], fieldnames: list[str], filename: str) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/customers")
def export_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).filter(Customer.tenant_id == current_user.tenant_id).all()
    rows = [
        {"id": c.id, "name": c.name, "email": c.email or "", "phone": c.phone or ""}
        for c in customers
    ]
    return csv_response(rows, ["id", "name", "email", "phone"], "customers.csv")


@router.get("/products")
def export_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.tenant_id == current_user.tenant_id).all()
    rows = [
        {"id": p.id, "name": p.name, "price": str(p.price), "cost": str(p.cost) if p.cost else ""}
        for p in products
    ]
    return csv_response(rows, ["id", "name", "price", "cost"], "products.csv")


@router.get("/orders")
def export_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = db.query(Order).filter(Order.tenant_id == current_user.tenant_id).all()
    rows = [
        {
            "id": o.id,
            "customer_id": o.customer_id or "",
            "total_amount": str(o.total_amount),
            "created_at": o.created_at.isoformat() if o.created_at else "",
        }
        for o in orders
    ]
    return csv_response(rows, ["id", "customer_id", "total_amount", "created_at"], "orders.csv")
