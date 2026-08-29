"""
Lightweight, non-ML analytics: customer segmentation and low-performer
detection. These are threshold/rule-based rather than model-based —
appropriate at small data volume, and honestly simpler problems than
forecasting. No sklearn needed here.
"""

from decimal import Decimal


def segment_customers(customer_order_counts: list[tuple[int, str, int, Decimal]]) -> dict:
    """
    customer_order_counts: list of (customer_id, name, order_count, total_spent)
    Returns customers grouped into simple segments.
    """
    new_customers = []
    repeat_customers = []
    high_value_customers = []

    if not customer_order_counts:
        return {
            "new_customers": [],
            "repeat_customers": [],
            "high_value_customers": [],
        }

    spend_values = [float(spent) for _, _, _, spent in customer_order_counts]
    avg_spend = sum(spend_values) / len(spend_values)

    for customer_id, name, order_count, total_spent in customer_order_counts:
        entry = {"customer_id": customer_id, "name": name, "order_count": order_count, "total_spent": str(total_spent)}

        if order_count <= 1:
            new_customers.append(entry)
        else:
            repeat_customers.append(entry)

        if float(total_spent) > avg_spend * 1.5:  # meaningfully above average
            high_value_customers.append(entry)

    return {
        "new_customers": new_customers,
        "repeat_customers": repeat_customers,
        "high_value_customers": high_value_customers,
    }


def detect_low_performers(product_sales: list[tuple[int, str, int, Decimal]]) -> dict:
    """
    product_sales: list of (product_id, name, quantity_sold, revenue)
    Flags products selling meaningfully below the tenant's average.
    """
    if not product_sales:
        return {"reliable": False, "reason": "No product sales data yet.", "low_performers": []}

    if len(product_sales) < 2:
        return {
            "reliable": False,
            "reason": "Need at least 2 products with sales to compare performance.",
            "low_performers": [],
        }

    revenues = [float(revenue) for _, _, _, revenue in product_sales]
    avg_revenue = sum(revenues) / len(revenues)
    threshold = avg_revenue * 0.5  # meaningfully below average

    low_performers = [
        {
            "product_id": product_id,
            "name": name,
            "quantity_sold": quantity_sold,
            "revenue": str(revenue),
        }
        for product_id, name, quantity_sold, revenue in product_sales
        if float(revenue) < threshold
    ]

    return {"reliable": True, "reason": None, "low_performers": low_performers}
