"""
RealityCheck core package.
"""

from src.product_search import search_product
from src.price_analysis import compare_prices
from src.discount_analysis import find_discounts
from src.review_analysis import analyze_reviews
from src.alternatives import find_alternatives
from src.spec_comparison import compare_specs
from src.value_scoring import calculate_value_score
from src.purchase_workflow import investigate_purchase
from src.safety import safety_manager, SafetyConfirmationManager

__all__ = [
    "search_product",
    "compare_prices",
    "find_discounts",
    "analyze_reviews",
    "find_alternatives",
    "compare_specs",
    "calculate_value_score",
    "investigate_purchase",
    "safety_manager",
    "SafetyConfirmationManager",
]
