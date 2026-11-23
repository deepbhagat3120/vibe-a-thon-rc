"""
Function 2: Price Analysis
Compares user-provided price against marketplace benchmark prices.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("realitycheck.price_analysis")


def compare_prices(product: Dict[str, Any], user_price: float) -> Dict[str, Any]:
    """
    Compares the user's offered purchase price against available market prices.

    Args:
        product: Product dictionary containing 'name', 'market_prices', 'mrp', etc.
        user_price: The price the user is currently seeing or considering.

    Returns:
        Structured dictionary conforming to price comparison specs.
    """
    if not isinstance(product, dict) or not product:
        return {
            "success": False,
            "error": "Invalid or empty product dictionary provided.",
            "user_price": user_price,
            "is_competitive": False,
            "competitiveness_tier": "UNKNOWN",
            "summary": "Product data unavailable for price comparison."
        }

    # Validate user price
    try:
        user_price = float(user_price)
    except (ValueError, TypeError):
        return {
            "success": False,
            "error": f"Invalid price format: {user_price}. Must be a valid positive number.",
            "user_price": 0.0,
            "is_competitive": False,
            "competitiveness_tier": "UNKNOWN",
            "summary": "User price must be a valid positive number."
        }

    if user_price <= 0:
        return {
            "success": False,
            "error": f"Invalid user price: {user_price}. Price must be greater than zero.",
            "user_price": user_price,
            "is_competitive": False,
            "competitiveness_tier": "UNKNOWN",
            "summary": "Price must be greater than zero."
        }

    market_entries = product.get("market_prices", [])
    valid_market_prices: List[float] = [
        float(entry["price"]) for entry in market_entries
        if isinstance(entry, dict) and entry.get("price") and float(entry.get("price", 0)) > 0
    ]

    # Handle scenario where market data is missing or incomplete (Scenario 5)
    if not valid_market_prices:
        return {
            "success": True,
            "user_price": user_price,
            "lowest_market_price": None,
            "average_market_price": None,
            "highest_market_price": None,
            "difference_from_lowest": None,
            "difference_from_average": None,
            "is_competitive": False,
            "competitiveness_tier": "UNKNOWN",
            "market_samples_count": 0,
            "price_breakdown": [],
            "summary": "No verified market price points exist in database for comparison.",
            "warning": "Market price data is incomplete. Price competitiveness cannot be validated."
        }

    lowest_price = min(valid_market_prices)
    highest_price = max(valid_market_prices)
    avg_price = round(sum(valid_market_prices) / len(valid_market_prices), 2)

    diff_from_lowest = round(user_price - lowest_price, 2)
    diff_from_avg = round(user_price - avg_price, 2)
    percent_diff_from_lowest = round(((user_price - lowest_price) / lowest_price) * 100, 2)

    # Competitiveness Logic:
    # EXCELLENT: user_price <= lowest market price
    # GOOD: user_price is within 3% above lowest price
    # FAIR: user_price is between lowest and average market price
    # OVERPRICED: user_price is significantly above average market price (> 5% above avg)
    if user_price <= lowest_price:
        tier = "EXCELLENT"
        is_comp = True
        summary = (
            f"Outstanding price! ₹{user_price:,.2f} is at or below the lowest available market rate "
            f"(₹{lowest_price:,.2f})."
        )
    elif user_price <= lowest_price * 1.03:
        tier = "GOOD"
        is_comp = True
        summary = (
            f"Very competitive! ₹{user_price:,.2f} is within 3% of the lowest market rate "
            f"(₹{lowest_price:,.2f})."
        )
    elif user_price <= avg_price:
        tier = "FAIR"
        is_comp = True
        summary = (
            f"Fair deal. ₹{user_price:,.2f} is below average market rate (₹{avg_price:,.2f}), "
            f"though a lower deal exists at ₹{lowest_price:,.2f}."
        )
    else:
        tier = "OVERPRICED"
        is_comp = False
        summary = (
            f"Overpriced. ₹{user_price:,.2f} is ₹{diff_from_lowest:,.2f} (+{percent_diff_from_lowest}%) "
            f"higher than the lowest market price of ₹{lowest_price:,.2f}."
        )

    breakdown = []
    for entry in market_entries:
        if isinstance(entry, dict) and "price" in entry:
            breakdown.append({
                "source": entry.get("source", "Retailer"),
                "price": float(entry["price"]),
                "difference": round(user_price - float(entry["price"]), 2),
                "in_stock": entry.get("in_stock", True)
            })

    return {
        "success": True,
        "user_price": user_price,
        "lowest_market_price": lowest_price,
        "average_market_price": avg_price,
        "highest_market_price": highest_price,
        "difference_from_lowest": diff_from_lowest,
        "difference_from_average": diff_from_avg,
        "difference_percent_lowest": percent_diff_from_lowest,
        "is_competitive": is_comp,
        "competitiveness_tier": tier,
        "market_samples_count": len(valid_market_prices),
        "price_breakdown": breakdown,
        "summary": summary
    }
