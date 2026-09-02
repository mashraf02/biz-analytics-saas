import csv
import io
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.core.limits import enforce_limit
from app.models.user import User
from app.models.customer import Customer
from app.models.tenant import Tenant

router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None

    class Config:
        from_attributes = True


class UploadResult(BaseModel):
    inserted: int
    failed: int
    errors: List[str]


@router.post("", response_model=CustomerOut)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    enforce_limit(db, Customer, current_user.tenant_id, tenant.plan, "max_customers", "customers")

    customer = Customer(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Customer).filter(Customer.tenant_id == current_user.tenant_id).all()


@router.post("/upload", response_model=UploadResult)
def upload_customers_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    inserted = 0
    errors: List[str] = []

    for row_number, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()
        if not name:
            errors.append(f"Row {row_number}: missing name, skipped")
            continue

        customer = Customer(
            tenant_id=current_user.tenant_id,
            name=name,
            email=(row.get("email") or "").strip() or None,
            phone=(row.get("phone") or "").strip() or None,
        )
        db.add(customer)
        inserted += 1

    db.commit()

    return UploadResult(inserted=inserted, failed=len(errors), errors=errors)
