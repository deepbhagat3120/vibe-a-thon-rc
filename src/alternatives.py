"""
Function 5: Alternative Discovery
Discovers comparable products in the same category within relevant price segments.
"""

import logging
from typing import Dict, Any, List, Optional
from src.product_search import load_dataset

logger = logging.getLogger("realitycheck.alternatives")


def find_alternatives(
    product: Dict[str, Any],
    dataset_path: Optional[str] = None,
    max_results: int = 3
) -> Dict[str, Any]:
    """
    Finds direct and value-oriented alternatives for the specified product.

    Args:
        product: Target product dictionary.
        dataset_path: Optional path to products.json.
        max_results: Maximum number of alternatives to return.

    Returns:
        Structured dictionary containing shortlist of alternative products.
    """
    if not isinstance(product, dict) or not product:
        return {
            "success": False,
            "error": "Invalid or empty product dictionary.",
            "category": "",
            "target_product_id": "",
            "alternatives": [],
            "count": 0,
            "notes": "Target product data unavailable."
        }

    target_id = product.get("id", "")
    target_category = product.get("category", "")
    target_price = float(product.get("current_price", 0) or product.get("mrp", 0))
    all_products = load_dataset(dataset_path)

    if not all_products:
        return {
            "success": True,
            "category": target_category,
            "target_product_id": target_id,
            "alternatives": [],
            "count": 0,
            "notes": "No alternative products found in database."
        }

    product_map = {p.get("id"): p for p in all_products}
    explicit_alt_ids = product.get("alternatives", [])

    candidates = []

    # 1. First prioritize explicitly linked alternatives
    for alt_id in explicit_alt_ids:
        if alt_id in product_map and alt_id != target_id:
            cand = product_map[alt_id]
            candidates.append(cand)

    # 2. If candidates are fewer than max_results, find category peers
    if len(candidates) < max_results:
        for p in all_products:
            p_id = p.get("id", "")
            if p_id == target_id or any(c.get("id") == p_id for c in candidates):
                continue
            if p.get("category", "").lower() == target_category.lower():
                candidates.append(p)

    # Shortlist and extract summary attributes
    shortlist = []
    for cand in candidates[:max_results]:
        cand_price = float(cand.get("current_price", 0) or cand.get("mrp", 0))
        cand_rating = float(cand.get("rating", 0.0))
        
        # Derive key differentiator
        if cand_price < target_price * 0.8:
            diff = f"More budget-friendly (₹{cand_price:,.0f} vs ₹{target_price:,.0f})"
        elif cand_price > target_price * 1.2:
            diff = f"Higher-tier premium option (₹{cand_price:,.0f})"
        elif cand_rating > float(product.get("rating", 0)):
            diff = f"Higher buyer satisfaction ({cand_rating}/5 vs {product.get('rating', 0)}/5)"
        else:
            pros = cand.get("pros", [])
            diff = pros[0] if pros else "Comparable alternative"

        shortlist.append({
            "id": cand.get("id", ""),
            "name": cand.get("name", ""),
            "brand": cand.get("brand", ""),
            "price": cand_price,
            "rating": cand_rating,
            "key_differentiator": diff,
            "specifications": cand.get("specifications", {})
        })

    notes = (
        f"Found {len(shortlist)} comparable alternative(s) in {target_category}."
        if shortlist else f"No direct alternatives found for category {target_category}."
    )

    return {
        "success": True,
        "category": target_category,
        "target_product_id": target_id,
        "alternatives": shortlist,
        "count": len(shortlist),
        "notes": notes
    }
