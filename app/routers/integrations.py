from typing import List
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.integration import Integration
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.integrations.facebook_mock import fetch_facebook_orders

router = APIRouter(prefix="/integrations/facebook", tags=["integrations"])


class ConnectResponse(BaseModel):
    connected: bool
    provider: str
    note: str


class SyncResult(BaseModel):
    orders_synced: int
    customers_created: int
    products_created: int


def get_or_create_integration(db: Session, tenant_id: int) -> Integration:
    integration = (
        db.query(Integration)
        .filter(Integration.tenant_id == tenant_id, Integration.provider == "facebook")
        .first()
    )
    if not integration:
        integration = Integration(tenant_id=tenant_id, provider="facebook", connected=False)
        db.add(integration)
        db.flush()
    return integration


@router.post("/connect", response_model=ConnectResponse)
def connect_facebook(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Real version: redirect the user to Facebook's OAuth consent screen here,
    # returning an authorization URL for the frontend to open.
    integration = get_or_create_integration(db, current_user.tenant_id)
    integration.connected = True
    integration.access_token = "mock-access-token"          # placeholder, no real auth yet
    integration.external_account_id = "mock-page-id-123"
    db.commit()

    return ConnectResponse(
        connected=True,
        provider="facebook",
        note="Mock connection established. Replace with real OAuth flow when Meta app is approved.",
    )


@router.post("/sync", response_model=SyncResult)
def sync_facebook_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    integration = get_or_create_integration(db, current_user.tenant_id)
    if not integration.connected:
        raise HTTPException(status_code=400, detail="Facebook is not connected for this tenant")

    raw_orders = fetch_facebook_orders(integration.external_account_id)

    orders_synced = 0
    customers_created = 0
    products_created = 0

    for raw_order in raw_orders:
        # Find or create the customer, scoped to this tenant
        customer = None
        if raw_order.get("customer_email"):
            customer = (
                db.query(Customer)
                .filter(
                    Customer.tenant_id == current_user.tenant_id,
                    Customer.email == raw_order["customer_email"],
                )
                .first()
            )
        if not customer:
            customer = Customer(
                tenant_id=current_user.tenant_id,
                name=raw_order["customer_name"],
                email=raw_order.get("customer_email"),
            )
            db.add(customer)
            db.flush()
            customers_created += 1

        order = Order(tenant_id=current_user.tenant_id, customer_id=customer.id, total_amount=0)
        db.add(order)
        db.flush()

        total = Decimal("0")
        for raw_item in raw_order["items"]:
            product = (
                db.query(Product)
                .filter(
                    Product.tenant_id == current_user.tenant_id,
                    Product.name == raw_item["product_name"],
                )
                .first()
            )
            if not product:
                product = Product(
                    tenant_id=current_user.tenant_id,
                    name=raw_item["product_name"],
                    price=Decimal(str(raw_item["unit_price"])),
                )
                db.add(product)
                db.flush()
                products_created += 1

            unit_price = Decimal(str(raw_item["unit_price"]))
            quantity = raw_item["quantity"]
            total += unit_price * quantity

            order_item = OrderItem(
                tenant_id=current_user.tenant_id,
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
            db.add(order_item)

        order.total_amount = total
        orders_synced += 1

    integration.last_synced_at = datetime.now(timezone.utc)
    db.commit()

    return SyncResult(
        orders_synced=orders_synced,
        customers_created=customers_created,
        products_created=products_created,
    )
