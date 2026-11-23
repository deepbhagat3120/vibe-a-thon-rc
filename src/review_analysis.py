"""
Function 4: Review Analysis
Analyzes sample customer reviews, extracts sentiment metrics, and surfaces recurring complaints.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("realitycheck.review_analysis")


def analyze_reviews(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes sample customer reviews for a product.
    
    Notice: Operates on sample/mock review data for hackathon demonstration.

    Args:
        product: Product dictionary containing 'reviews', 'rating', 'review_count', 'pros', 'cons', 'recurring_complaints'.

    Returns:
        Structured review analysis dictionary.
    """
    if not isinstance(product, dict) or not product:
        return {
            "success": False,
            "error": "Invalid or empty product dictionary.",
            "total_reviews_analyzed": 0,
            "dataset_rating": 0.0,
            "sentiment_distribution": {"positive": 0.0, "neutral": 0.0, "negative": 0.0},
            "is_data_sufficient": False,
            "sentiment_summary": "No product data available.",
            "warnings": ["Missing product data."]
        }

    reviews: List[Dict[str, Any]] = product.get("reviews", [])
    rating = float(product.get("rating", 0.0))
    review_count = int(product.get("review_count", 0))

    # Scenario 4: Insufficient or missing review data
    if not reviews and review_count == 0:
        return {
            "success": True,
            "total_reviews_analyzed": 0,
            "dataset_rating": 0.0,
            "sentiment_distribution": {
                "positive": 0.0,
                "neutral": 0.0,
                "negative": 0.0
            },
            "common_positives": [],
            "common_negatives": [],
            "recurring_complaints": [],
            "is_data_sufficient": False,
            "sentiment_summary": "Insufficient review data. No verified customer reviews exist in the dataset.",
            "warnings": [
                "Product has ZERO customer reviews. Reliability and long-term durability cannot be verified from buyer feedback."
            ],
            "data_notice": "DEMO MOCK DATA - Insufficient data scenario"
        }

    pos_count = 0
    neu_count = 0
    neg_count = 0

    for r in reviews:
        sent = r.get("sentiment", "").lower()
        stars = float(r.get("rating", 3.0))
        if sent == "positive" or stars >= 4.0:
            pos_count += 1
        elif sent == "negative" or stars <= 2.0:
            neg_count += 1
        else:
            neu_count += 1

    total = max(len(reviews), 1)
    pos_pct = round((pos_count / total) * 100.0, 1)
    neu_pct = round((neu_count / total) * 100.0, 1)
    neg_pct = round((neg_count / total) * 100.0, 1)

    # Use curated product pros/cons or review insights
    positives = product.get("pros", [])
    negatives = product.get("cons", [])
    recurring = product.get("recurring_complaints", [])

    if not positives and reviews:
        positives = [r.get("title") for r in reviews if r.get("sentiment") == "positive"][:3]
    if not negatives and reviews:
        negatives = [r.get("title") for r in reviews if r.get("sentiment") == "negative"][:3]

    warnings = []
    if len(reviews) < 3:
        warnings.append(f"Small sample size ({len(reviews)} reviews). Confidence in review trends is reduced.")
    if neg_pct >= 30.0:
        warnings.append(f"High negative sentiment ({neg_pct}%). Frequent quality/experience issues reported.")

    if pos_pct >= 70.0:
        sentiment_summary = (
            f"Overwhelmingly positive ({pos_pct}% positive). "
            f"Average score {rating}/5 based on {review_count:,} ratings."
        )
    elif neg_pct >= 40.0:
        sentiment_summary = (
            f"High dissatisfaction detected ({neg_pct}% negative). "
            f"Average score {rating}/5 with recurring issues."
        )
    else:
        sentiment_summary = (
            f"Mixed feedback ({pos_pct}% positive, {neu_pct}% neutral, {neg_pct}% negative). "
            f"Rating: {rating}/5."
        )

    return {
        "success": True,
        "total_reviews_analyzed": len(reviews),
        "total_store_ratings": review_count,
        "dataset_rating": rating,
        "sentiment_distribution": {
            "positive": pos_pct,
            "neutral": neu_pct,
            "negative": neg_pct
        },
        "common_positives": positives,
        "common_negatives": negatives,
        "recurring_complaints": recurring,
        "is_data_sufficient": len(reviews) >= 3 or review_count >= 50,
        "sentiment_summary": sentiment_summary,
        "warnings": warnings,
        "data_notice": "DEMO MOCK DATA - Curated sample reviews for demonstration purposes"
    }
