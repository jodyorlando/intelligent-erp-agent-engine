from typing import Dict, Any
from langchain_core.tools import tool
from app.services.redis_cache import get_cached_tool_result, set_cached_tool_result


@tool
async def check_inventory_stock(item_code: str) -> Dict[str, Any]:
    """
    Check current available stock quantity and warehouse location for an item code.
    """
    tool_name = "check_inventory_stock"
    args = {"item_code": item_code}

    #1. Check Redis Cache
    cached_result = await get_cached_tool_result(tool_name, args)
    if cached_result:
        return f"[CACHED] {cached_result}"

    # 2. Simulate Database Lookup (Cache Miss)
    # In production, this queries PostgreSQL via asyncpg
    stock_database = {
        "6204-2RS": {"stock": 450, "unit_price": 4.50, "location": "Warehouse A-12"},
        "6309-ZZ": {"stock": 120, "unit_price": 18.75, "location": "Warehouse B-04"},
        "LM8UU": {"stock": 850, "unit_price": 1.20, "location": "Warehouse A-01"},
    }

    item_data = stock_database.get(item_code.strip().upper())

    if not item_data:
        result = f"Item '{item_code}' not found in inventory catalog."
    else:
        result = (
            f"The stock details for item **{item_code}** are as follows:\n"
            f"- **Stock Quantity:** {item_data['stock']} units\n"
            f"- **Unit Price:** ${item_data['unit_price']:.2f}\n"
            f"- **Location:** {item_data['location']}"
        )

    # 3. Store Result in Redis Cache with 60-second TTL
    await set_cached_tool_result(tool_name, args, result, ttl_seconds=60)
    return result


@tool
async def calculate_order_quote(item_code: str, quantity: int, customer_tier: str = "standard") -> Dict[str, Any]:
    """
    Calculate an order quote with bulk volume discounts based on customer tier.
    """
    tool_name = "calculate_order_quote"
    args = {"item_code": item_code, "quantity": quantity, "customer_tier": customer_tier}

    # 1. Check Redis Cache
    cached_result = await get_cached_tool_result(tool_name, args)
    if cached_result:
        return f"[CACHED] {cached_result}"

    # 2. Calculation Logic (Cache Miss)
    base_prices = {"6204-2RS": 4.50, "6309-ZZ": 18.75, "LM8UU": 1.20}
    unit_price = base_prices.get(item_code.upper(), 10.00)

    # Determine Discount Tier
    discount = 0.0
    if customer_tier.upper() == "VIP":
        discount += 0.10
    elif customer_tier.upper() == "WHOLESALE":
        discount += 0.15

    if quantity >= 100:
        discount += 0.05

    total_price = (unit_price * quantity) * (1 - discount)

    result = (f"Order Quote for item **{item_code}** ({quantity} units, Tier: {customer_tier}):\n"
        f"- **Unit Base Price:** ${unit_price:.2f}\n"
        f"- **Discount Applied:** {int(discount * 100)}%\n"
        f"- **Total Quote:** ${total_price:.2f}"
        )

    # 3. Store Result in Redis Cache with 120-second TL
    await set_cached_tool_result(tool_name, args, result, ttl_seconds=120)
    return result    