"""
Function 7: Value Scoring
Computes a transparent, deterministic 0–100 value-for-money score.
Formula:
    Value Score = (Price Competitiveness × 0.40) + (Review Sentiment × 0.30) + (Features & Specs × 0.30)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("realitycheck.value_scoring")


def calculate_value_score(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a deterministic 0-100 value score with a full mathematical breakdown.

    Args:
        product_data: Dictionary containing:
            - price_analysis: Output from compare_prices()
            - review_analysis: Output from analyze_reviews()
            - spec_comparison: Output from compare_specs() (optional)
            - product: Product dictionary

    Returns:
        Structured dictionary with overall_score, component scores, and explanation.
    """
    price_data = product_data.get("price_analysis", {})
    review_data = product_data.get("review_analysis", {})
    spec_data = product_data.get("spec_comparison", {})
    product = product_data.get("product", {})

    # =========================================================================
    # 1. Price Competitiveness Score (Weight: 40%)
    # =========================================================================
    price_tier = price_data.get("competitiveness_tier", "UNKNOWN")
    diff_lowest_pct = price_data.get("difference_percent_lowest", 0.0)

    if price_tier == "EXCELLENT":
        # Price is at or below lowest market benchmark
        price_score = 96.0
    elif price_tier == "GOOD":
        # Within 3% of lowest
        price_score = 88.0
    elif price_tier == "FAIR":
        # Under average market rate
        price_score = 74.0
    elif price_tier == "OVERPRICED":
        if diff_lowest_pct > 30:
            price_score = 30.0
        elif diff_lowest_pct > 15:
            price_score = 45.0
        else:
            price_score = 58.0
    else:  # UNKNOWN
        price_score = 50.0  # Neutral baseline when price data is unavailable

    # =========================================================================
    # 2. Review Sentiment Score (Weight: 30%)
    # =========================================================================
    is_review_sufficient = review_data.get("is_data_sufficient", False)
    if not is_review_sufficient:
        # Penalize slightly or hold at neutral baseline if 0 reviews
        review_score = 50.0
    else:
        rating = float(review_data.get("dataset_rating", product.get("rating", 3.0)))
        sentiment = review_data.get("sentiment_distribution", {})
        pos_pct = float(sentiment.get("positive", 60.0))
        neg_pct = float(sentiment.get("negative", 15.0))

        # Rating contributes 60% of review subscore (5.0 stars = 60 pts)
        rating_pts = (min(max(rating, 0.0), 5.0) / 5.0) * 60.0
        
        # Sentiment net contributes 40% of review subscore
        sentiment_pts = ((pos_pct - neg_pct + 100.0) / 200.0) * 40.0
        
        review_score = round(min(max(rating_pts + sentiment_pts, 0.0), 100.0), 1)

    # =========================================================================
    # 3. Features & Specifications Score (Weight: 30%)
    # =========================================================================
    pros_count = len(product.get("pros", []))
    cons_count = len(product.get("cons", []))
    strengths_count = len(spec_data.get("key_strengths", []))
    tradeoffs_count = len(spec_data.get("key_tradeoffs", []))

    # Base feature score = 70
    base_feature = 70.0
    # Strengths boost
    feature_bonus = (strengths_count * 5.0) + (max(pros_count - cons_count, 0) * 3.0)
    # Tradeoffs penalty
    feature_penalty = (tradeoffs_count * 5.0) + (max(cons_count - pros_count, 0) * 3.0)
    
    spec_score = round(min(max(base_feature + feature_bonus - feature_penalty, 25.0), 100.0), 1)

    # =========================================================================
    # 4. Overall Weighted Score Calculation
    # =========================================================================
    weighted_price = round(price_score * 0.40, 2)
    weighted_review = round(review_score * 0.30, 2)
    weighted_spec = round(spec_score * 0.30, 2)

    overall_score = int(round(weighted_price + weighted_review + weighted_spec))
    overall_score = min(max(overall_score, 0), 100)

    # Explanation construction
    explanation = (
        f"Overall Value Score: {overall_score}/100\n\n"
        f"• Price Competitiveness: {price_score:.1f}/100 (40% wt = {weighted_price} pts)\n"
        f"• Review Sentiment: {review_score:.1f}/100 (30% wt = {weighted_review} pts)\n"
        f"• Specification & Feature Balance: {spec_score:.1f}/100 (30% wt = {weighted_spec} pts)"
    )

    return {
        "overall_score": overall_score,
        "price_competitiveness_score": price_score,
        "review_sentiment_score": review_score,
        "specs_features_score": spec_score,
        "weights": {
            "price_weight": 0.40,
            "review_weight": 0.30,
            "spec_weight": 0.30
        },
        "weighted_points": {
            "price_pts": weighted_price,
            "review_pts": weighted_review,
            "spec_pts": weighted_spec
        },
        "explanation": explanation
    }
