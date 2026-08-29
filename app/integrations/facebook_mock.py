"""
Mock Facebook/Instagram data source.

This mimics the *shape* of what Meta's Graph API would return for a business
Page's orders/sales data. Swapping this for the real API later means replacing
only this function's internals — everything downstream (validation, insertion)
stays the same.
"""

from datetime import datetime, timezone


def fetch_facebook_orders(external_account_id: str) -> list[dict]:
    # In a real integration, this would be an authenticated request to
    # Meta's Graph API using the stored access_token, something like:
    #   GET https://graph.facebook.com/v19.0/{page_id}/commerce_orders
    # For now, we return realistic mock data in the same shape.
    return [
        {
            "fb_order_id": "fb_order_1001",
            "customer_name": "Nusrat Jahan",
            "customer_email": "nusrat@example.com",
            "items": [
                {"product_name": "Vanilla Cupcake", "quantity": 6, "unit_price": 60.00},
            ],
            "created_time": datetime.now(timezone.utc).isoformat(),
        },
        {
            "fb_order_id": "fb_order_1002",
            "customer_name": "Tanvir Ahmed",
            "customer_email": None,
            "items": [
                {"product_name": "Chocolate Cake", "quantity": 1, "unit_price": 850.00},
                {"product_name": "Vanilla Cupcake", "quantity": 12, "unit_price": 60.00},
            ],
            "created_time": datetime.now(timezone.utc).isoformat(),
        },
    ]
