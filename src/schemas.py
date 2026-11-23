"""
Data schemas and type models for RealityCheck.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class MarketPrice(BaseModel):
    source: str
    price: float
    in_stock: bool = True


class DiscountOffer(BaseModel):
    type: str  # e.g., "bank", "coupon", "exchange"
    description: str
    amount: Optional[float] = None
    percent: Optional[float] = None
    max_discount: Optional[float] = None
    code: Optional[str] = None


class ReviewItem(BaseModel):
    rating: float
    title: str
    comment: str
    sentiment: Literal["positive", "neutral", "negative"]


class Product(BaseModel):
    id: str
    brand: str
    name: str
    category: str
    mrp: float
    current_price: float
    market_prices: List[MarketPrice] = Field(default_factory=list)
    discounts: List[DiscountOffer] = Field(default_factory=list)
    rating: float = 0.0
    review_count: int = 0
    reviews: List[ReviewItem] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    recurring_complaints: List[str] = Field(default_factory=list)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    alternatives: List[str] = Field(default_factory=list)
    is_mock: bool = True
    mock_notice: str = "DEMO MOCK DATA"


class PriceAnalysisResult(BaseModel):
    user_price: float
    lowest_market_price: Optional[float] = None
    average_market_price: Optional[float] = None
    highest_market_price: Optional[float] = None
    difference_from_lowest: Optional[float] = None
    difference_from_average: Optional[float] = None
    is_competitive: bool = False
    competitiveness_tier: Literal["EXCELLENT", "GOOD", "FAIR", "OVERPRICED", "UNKNOWN"]
    market_samples_count: int = 0
    price_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str


class DiscountAnalysisResult(BaseModel):
    original_price: float
    best_discount_saving: float = 0.0
    applied_discount_type: Optional[str] = None
    applied_discount_code: Optional[str] = None
    effective_price: float
    all_available_discounts: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    has_discounts: bool = False


class ReviewAnalysisResult(BaseModel):
    total_reviews_analyzed: int
    dataset_rating: float
    sentiment_distribution: Dict[str, float]  # e.g., {"positive": 60.0, "neutral": 20.0, ...}
    common_positives: List[str] = Field(default_factory=list)
    common_negatives: List[str] = Field(default_factory=list)
    recurring_complaints: List[str] = Field(default_factory=list)
    is_data_sufficient: bool = True
    sentiment_summary: str
    warnings: List[str] = Field(default_factory=list)


class AlternativeItem(BaseModel):
    id: str
    name: str
    brand: str
    price: float
    rating: float
    key_differentiator: str


class AlternativesResult(BaseModel):
    category: str
    target_product_id: str
    alternatives: List[AlternativeItem] = Field(default_factory=list)
    count: int = 0
    notes: str = ""


class SpecComparisonResult(BaseModel):
    target_product_name: str
    compared_attributes: List[str] = Field(default_factory=list)
    spec_matrix: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    key_strengths: List[str] = Field(default_factory=list)
    key_tradeoffs: List[str] = Field(default_factory=list)


class ValueScoreResult(BaseModel):
    overall_score: int  # 0 to 100
    price_competitiveness_score: float  # weight 40%
    review_sentiment_score: float       # weight 30%
    specs_features_score: float         # weight 30%
    explanation: str
    breakdown_details: Dict[str, Any] = Field(default_factory=dict)


class InvestigationResult(BaseModel):
    product: Dict[str, Any]
    price_analysis: Optional[PriceAnalysisResult] = None
    discount_analysis: Optional[DiscountAnalysisResult] = None
    review_analysis: Optional[ReviewAnalysisResult] = None
    alternatives: List[AlternativeItem] = Field(default_factory=list)
    spec_comparison: Optional[SpecComparisonResult] = None
    value_score: int = 0
    value_score_details: Optional[ValueScoreResult] = None
    verdict: Literal["BUY", "WAIT", "AVOID"]
    confidence: float  # 0.0 to 1.0
    verdict_reasoning: str
    warnings: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    data_source_type: str = "mock"


class SafetyActionRequest(BaseModel):
    action_type: Literal["CREATE_PRICE_ALERT", "ADD_TO_WISHLIST", "ADD_TO_CART", "PURCHASE"]
    product_id: str
    product_name: str
    target_price: Optional[float] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["PREPARED", "CONFIRMED", "REJECTED", "EXECUTED"] = "PREPARED"
    requires_confirmation: bool = True
    user_confirmed: Optional[bool] = None
    confirmation_message: str
    execution_result: Optional[str] = None
