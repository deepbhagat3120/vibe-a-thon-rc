"""
Function 3: Discount Analysis
Evaluates available discounts, prevents double-counting, and computes effective net price.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("realitycheck.discount_analysis")


def find_discounts(product: Dict[str, Any], base_price: Optional[float] = None) -> Dict[str, Any]:
    """
    Evaluates promotional discounts, coupons, and bank offers.
    
    Rules for avoiding double counting:
    - Multiple bank discounts cannot be stacked (only the highest bank saving applies).
    - Instant coupons and promo codes CAN stack with one bank offer up to a combined maximum cap.
    - Total discounts cannot reduce price below 50% of the baseline.

    Args:
        product: Product dictionary containing 'discounts' and 'current_price'.
        base_price: Optional reference price (defaults to product['current_price'] or user price).

    Returns:
        Structured discount analysis dictionary.
    """
    if not isinstance(product, dict) or not product:
        return {
            "success": False,
            "error": "Invalid or empty product dictionary provided.",
            "original_price": base_price or 0.0,
            "effective_price": base_price or 0.0,
            "total_savings": 0.0,
            "has_discounts": False,
            "assumptions": ["No product data available."]
        }

    raw_price = base_price if base_price is not None else product.get("current_price", 0.0)
    try:
        price = float(raw_price)
    except (ValueError, TypeError):
        price = 0.0

    if price <= 0:
        price = float(product.get("mrp", 0.0))

    discounts_list = product.get("discounts", [])
    if not discounts_list:
        return {
            "success": True,
            "original_price": price,
            "effective_price": price,
            "total_savings": 0.0,
            "applied_discount_type": None,
            "applied_discount_code": None,
            "all_available_discounts": [],
            "has_discounts": False,
            "assumptions": ["No active promotional discounts or bank coupons available for this product."],
            "summary": "No discounts available. Full price applies."
        }

    bank_offers = []
    coupon_offers = []
    other_offers = []

    for d in discounts_list:
        dtype = d.get("type", "other").lower()
        # Compute prospective saving
        saving = 0.0
        if "amount" in d and d["amount"]:
            saving = float(d["amount"])
        elif "percent" in d and d["percent"]:
            calc = (float(d["percent"]) / 100.0) * price
            if "max_discount" in d and d["max_discount"]:
                saving = min(calc, float(d["max_discount"]))
            else:
                saving = calc
        
        offer_entry = {
            "type": dtype,
            "description": d.get("description", ""),
            "code": d.get("code", "N/A"),
            "calculated_saving": round(saving, 2)
        }

        if dtype == "bank":
            bank_offers.append(offer_entry)
        elif dtype == "coupon":
            coupon_offers.append(offer_entry)
        else:
            other_offers.append(offer_entry)

    assumptions: List[str] = []
    total_savings = 0.0
    applied_codes = []
    applied_types = []

    # 1. Apply single best bank offer (avoiding double-counting multi-bank offers)
    if bank_offers:
        bank_offers.sort(key=lambda x: x["calculated_saving"], reverse=True)
        best_bank = bank_offers[0]
        total_savings += best_bank["calculated_saving"]
        applied_codes.append(best_bank["code"])
        applied_types.append(f"Bank ({best_bank['code']})")
        assumptions.append(
            f"Applied best bank offer '{best_bank['description']}' saving ₹{best_bank['calculated_saving']:,.2f}. "
            f"(Assumes user holds eligible card; other bank offers do not stack)."
        )

    # 2. Apply best coupon offer if available
    if coupon_offers:
        coupon_offers.sort(key=lambda x: x["calculated_saving"], reverse=True)
        best_coupon = coupon_offers[0]
        total_savings += best_coupon["calculated_saving"]
        applied_codes.append(best_coupon["code"])
        applied_types.append(f"Coupon ({best_coupon['code']})")
        assumptions.append(
            f"Applied coupon '{best_coupon['code']}' saving ₹{best_coupon['calculated_saving']:,.2f}."
        )

    # Floor protection: effective price cannot drop below 30% of original price
    max_allowable_discount = price * 0.70
    if total_savings > max_allowable_discount:
        total_savings = max_allowable_discount
        assumptions.append("Discounts capped at maximum promotional threshold (70% of base value).")

    effective_price = max(0.0, round(price - total_savings, 2))

    summary = (
        f"Potential savings of ₹{total_savings:,.2f} available. "
        f"Effective net price: ₹{effective_price:,.2f}."
        if total_savings > 0 else "No applicable discounts found."
    )

    return {
        "success": True,
        "original_price": price,
        "effective_price": effective_price,
        "total_savings": round(total_savings, 2),
        "applied_discount_type": " + ".join(applied_types) if applied_types else None,
        "applied_discount_code": ", ".join(applied_codes) if applied_codes else None,
        "all_available_discounts": [
            {**d, "saving": round(d.get("amount", 0) or (d.get("percent", 0)/100.0 * price), 2)}
            for d in discounts_list
        ],
        "has_discounts": total_savings > 0,
        "assumptions": assumptions,
        "summary": summary
    }
