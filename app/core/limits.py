"""
Plan-based usage limits.

No real billing is wired up here — this defines what a subscription system
would enforce once real payments exist. Free tier gets restrictive limits;
"pro" is unlimited for now. Swapping in real billing later only means
changing how `tenant.plan` gets set (e.g. via a Stripe webhook), not this
enforcement logic.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

PLAN_LIMITS = {
    "free": {"max_products": 10, "max_customers": 20, "max_orders_per_month": 30},
    "pro": {"max_products": None, "max_customers": None, "max_orders_per_month": None},
}


def get_limits(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


def enforce_limit(db: Session, model, tenant_id: int, plan: str, limit_key: str, resource_name: str):
    limit = get_limits(plan).get(limit_key)
    if limit is None:
        return  # unlimited on this plan

    current_count = db.query(model).filter(model.tenant_id == tenant_id).count()
    if current_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Free plan limit reached: max {limit} {resource_name}. Upgrade to Pro for unlimited.",
        )
