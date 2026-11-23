"""
Tests for Function 4: analyze_reviews()
"""

import pytest
from src.review_analysis import analyze_reviews


def test_analyze_reviews_positive():
    product = {
        "id": "p1",
        "name": "Super Sound 1",
        "rating": 4.5,
        "review_count": 500,
        "reviews": [
            {"rating": 5, "title": "Great", "comment": "Loved it", "sentiment": "positive"},
            {"rating": 4, "title": "Good", "comment": "Nice quality", "sentiment": "positive"},
            {"rating": 5, "title": "Awesome", "comment": "Best ever", "sentiment": "positive"}
        ],
        "pros": ["Battery", "Audio"],
        "cons": ["Plastic"],
        "recurring_complaints": []
    }
    result = analyze_reviews(product)
    assert result["success"] is True
    assert result["is_data_sufficient"] is True
    assert result["sentiment_distribution"]["positive"] == 100.0
    assert "Battery" in result["common_positives"]


def test_analyze_reviews_insufficient_data():
    empty_product = {
        "id": "p2",
        "name": "No Review Gadget",
        "rating": 0,
        "review_count": 0,
        "reviews": [],
        "pros": [],
        "cons": [],
        "recurring_complaints": []
    }
    result = analyze_reviews(empty_product)
    assert result["success"] is True
    assert result["is_data_sufficient"] is False
    assert len(result["warnings"]) > 0
    assert result["total_reviews_analyzed"] == 0
