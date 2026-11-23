"""
Phase 3: High-Level Composed Workflow
investigate_purchase(product_name, user_price, user_requirements=None)

Orchestrates 7 internal modules into a single resilient purchasing intelligence report.
"""

import time
import logging
from typing import Dict, Any, Optional, List

from src.product_search import search_product
from src.price_analysis import compare_prices
from src.discount_analysis import find_discounts
from src.review_analysis import analyze_reviews
from src.alternatives import find_alternatives
from src.spec_comparison import compare_specs
from src.value_scoring import calculate_value_score

logger = logging.getLogger("realitycheck.purchase_workflow")


def investigate_purchase(
    product_name: str,
    user_price: float,
    user_requirements: Optional[str] = None,
    dataset_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes an end-to-end purchasing investigation for a target product.
    
    Steps executed internally:
        1. Product Identification
        2. Price Comparison
        3. Discount Analysis
        4. Review & Sentiment Analysis
        5. Alternative Product Discovery
        6. Specification Comparison
        7. Value Score Calculation
        8. Evidence-based Recommendation (BUY / WAIT / AVOID)

    Resilience features:
        - Catches step failures gracefully without aborting the entire report.
        - Accurately tracks completed_steps vs failed_steps.
        - Downgrades confidence proportionally to missing data points.
        - Highlights explicit data warnings.

    Args:
        product_name: Product query to search for.
        user_price: The price offered to or considered by the user.
        user_requirements: Optional user preference (e.g. 'battery life', 'budget', 'gaming').
        dataset_path: Optional override for the product database.

    Returns:
        Structured JSON-compatible dictionary.
    """
    start_time = time.perf_counter()
    completed_steps: List[str] = []
    failed_steps: List[str] = []
    warnings: List[str] = []
    confidence = 1.0

    # -------------------------------------------------------------------------
    # Step 1: Product Identification
    # -------------------------------------------------------------------------
    search_res = {}
    try:
        search_res = search_product(product_name, dataset_path=dataset_path, fallback_price=user_price)
        if not search_res.get("found") or not search_res.get("product"):
            failed_steps.append("product_identification")
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": False,
                "product": None,
                "price_analysis": None,
                "discount_analysis": None,
                "review_analysis": None,
                "alternatives": [],
                "spec_comparison": None,
                "value_score": 0,
                "verdict": "AVOID",
                "confidence": 0.0,
                "verdict_reasoning": f"Product '{product_name}' could not be identified in the catalog.",
                "warnings": [f"Could not locate '{product_name}' in catalog. Suggestions: {', '.join(search_res.get('candidate_names', []))}"],
                "failed_steps": failed_steps,
                "completed_steps": completed_steps,
                "execution_time_ms": elapsed,
                "data_source_type": "mock"
            }
        product = search_res["product"]
        completed_steps.append("product_identification")
        if search_res.get("is_dynamic"):
            warnings.append("DYNAMIC DEMO ESTIMATE: This product is not in the fixed benchmark catalog; price benchmarks and reviews were dynamically synthesized.")
        match_conf = search_res.get("match_confidence", 1.0)
        if match_conf < 0.8:
            confidence -= 0.10
            warnings.append(f"Fuzzy name match confidence is {match_conf*100:.0f}%. Matched to '{product.get('name')}'.")
    except Exception as e:
        logger.error(f"Error in product identification: {e}")
        failed_steps.append("product_identification")
        return {
            "success": False,
            "product": None,
            "verdict": "AVOID",
            "confidence": 0.0,
            "verdict_reasoning": f"Critical error in product identification: {str(e)}",
            "warnings": [str(e)],
            "failed_steps": failed_steps,
            "completed_steps": completed_steps,
            "data_source_type": "mock"
        }

    # -------------------------------------------------------------------------
    # Step 2: Price Comparison
    # -------------------------------------------------------------------------
    price_analysis = None
    try:
        price_analysis = compare_prices(product, user_price)
        if price_analysis.get("success"):
            completed_steps.append("price_comparison")
            if price_analysis.get("competitiveness_tier") == "UNKNOWN":
                confidence -= 0.25
                warnings.append("Market price benchmarks are incomplete. Price competitiveness is unverified.")
        else:
            failed_steps.append("price_comparison")
            warnings.append(f"Price analysis issue: {price_analysis.get('error')}")
            confidence -= 0.20
    except Exception as e:
        logger.error(f"Error in price comparison: {e}")
        failed_steps.append("price_comparison")
        warnings.append(f"Price comparison error: {str(e)}")
        confidence -= 0.20

    # -------------------------------------------------------------------------
    # Step 3: Discount Analysis
    # -------------------------------------------------------------------------
    discount_analysis = None
    try:
        discount_analysis = find_discounts(product, base_price=user_price)
        completed_steps.append("discount_analysis")
    except Exception as e:
        logger.error(f"Error in discount analysis: {e}")
        failed_steps.append("discount_analysis")
        warnings.append(f"Discount analysis error: {str(e)}")
        confidence -= 0.10

    # -------------------------------------------------------------------------
    # Step 4: Review Analysis
    # -------------------------------------------------------------------------
    review_analysis = None
    try:
        review_analysis = analyze_reviews(product)
        if review_analysis.get("success"):
            completed_steps.append("review_analysis")
            if not review_analysis.get("is_data_sufficient"):
                confidence -= 0.25
                warnings.append("Zero or insufficient customer reviews available. Buyer sentiment is uncertain.")
            if review_analysis.get("warnings"):
                warnings.extend(review_analysis["warnings"])
        else:
            failed_steps.append("review_analysis")
            confidence -= 0.20
    except Exception as e:
        logger.error(f"Error in review analysis: {e}")
        failed_steps.append("review_analysis")
        warnings.append(f"Review analysis error: {str(e)}")
        confidence -= 0.20

    # -------------------------------------------------------------------------
    # Step 5: Alternative Discovery
    # -------------------------------------------------------------------------
    alternatives_raw = None
    alternatives_list = []
    try:
        alternatives_raw = find_alternatives(product, dataset_path=dataset_path, max_results=3)
        alternatives_list = alternatives_raw.get("alternatives", [])
        completed_steps.append("find_alternatives")
        if not alternatives_list:
            warnings.append(f"No direct competitors found in category {product.get('category')}.")
    except Exception as e:
        logger.error(f"Error finding alternatives: {e}")
        failed_steps.append("find_alternatives")
        warnings.append(f"Alternatives discovery error: {str(e)}")
        confidence -= 0.10

    # -------------------------------------------------------------------------
    # Step 6: Specification Comparison
    # -------------------------------------------------------------------------
    spec_comparison = None
    try:
        spec_comparison = compare_specs(product, alternatives_list)
        completed_steps.append("compare_specs")
    except Exception as e:
        logger.error(f"Error comparing specs: {e}")
        failed_steps.append("compare_specs")
        warnings.append(f"Specification comparison error: {str(e)}")
        confidence -= 0.10

    # -------------------------------------------------------------------------
    # Step 7: Value Scoring
    # -------------------------------------------------------------------------
    value_scoring_res = None
    value_score = 50
    try:
        pipeline_data = {
            "product": product,
            "price_analysis": price_analysis or {},
            "review_analysis": review_analysis or {},
            "spec_comparison": spec_comparison or {}
        }
        value_scoring_res = calculate_value_score(pipeline_data)
        value_score = value_scoring_res.get("overall_score", 50)
        completed_steps.append("calculate_value_score")
    except Exception as e:
        logger.error(f"Error in value scoring: {e}")
        failed_steps.append("calculate_value_score")
        warnings.append(f"Value scoring calculation error: {str(e)}")
        confidence -= 0.20

    # -------------------------------------------------------------------------
    # Step 8: Final Recommendation Verdict & Reasoning
    # -------------------------------------------------------------------------
    tier = (price_analysis or {}).get("competitiveness_tier", "UNKNOWN")
    lowest_market = (price_analysis or {}).get("lowest_market_price")
    review_neg_pct = (review_analysis or {}).get("sentiment_distribution", {}).get("negative", 0.0)

    # Consider user requirements if provided
    req_match = True
    if user_requirements:
        req_lower = user_requirements.lower()
        if "battery" in req_lower and product.get("category") == "Headphones":
            bat = product.get("specifications", {}).get("battery_life_hours", 0)
            if bat < 30:
                warnings.append(f"User requested good battery, but {product.get('name')} offers {bat}h.")
        if "budget" in req_lower and tier == "OVERPRICED":
            warnings.append("User requested budget-friendly purchase, but item is marked above market rates.")

    # Decision Matrix
    if value_score >= 75 and tier in ["EXCELLENT", "GOOD"]:
        verdict = "BUY"
        reasoning = (
            f"Strong BUY recommendation. {product.get('name')} earns a high value score of {value_score}/100. "
            f"Your price of ₹{user_price:,.2f} is highly competitive against market benchmarks "
            f"(lowest: ₹{lowest_market:,.2f} if known), backed by positive buyer sentiment."
        )
    elif tier == "OVERPRICED" and lowest_market and user_price > lowest_market * 1.10:
        verdict = "WAIT"
        reasoning = (
            f"WAIT recommended. The product itself is reputable, but your price of ₹{user_price:,.2f} is "
            f"substantially higher than the available lowest market price of ₹{lowest_market:,.2f}. "
            f"Consider waiting for price drops or purchasing from a cheaper retailer."
        )
    elif review_neg_pct >= 40.0 or value_score < 50:
        verdict = "AVOID"
        reasoning = (
            f"AVOID recommendation. Value score is low ({value_score}/100) and customer sentiment exhibits "
            f"concerning failure/dissatisfaction rates ({review_neg_pct:.0f}% negative feedback). "
            f"Consider better-rated alternatives in this segment."
        )
    elif value_score >= 60:
        verdict = "WAIT"
        reasoning = (
            f"WAIT recommended. Moderate value score of {value_score}/100. "
            f"While specifications are sound, better discounts or alternative deals are expected soon."
        )
    else:
        verdict = "WAIT"
        reasoning = (
            f"WAIT recommended. The product is rated {value_score}/100 with trade-offs. "
            f"Review the competing alternatives before finalizing your decision."
        )

    # Clamp confidence
    confidence = max(0.20, min(1.0, round(confidence, 2)))
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "success": True,
        "product": product,
        "price_analysis": price_analysis,
        "discount_analysis": discount_analysis,
        "review_analysis": review_analysis,
        "alternatives": alternatives_list,
        "spec_comparison": spec_comparison,
        "value_score": value_score,
        "value_score_details": value_scoring_res,
        "verdict": verdict,
        "confidence": confidence,
        "verdict_reasoning": reasoning,
        "warnings": warnings,
        "failed_steps": failed_steps,
        "completed_steps": completed_steps,
        "execution_time_ms": elapsed_ms,
        "data_source_type": "mock"
    }
