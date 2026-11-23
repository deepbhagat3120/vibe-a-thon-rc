"""
Unit tests for Dynamic Catalog Synthesis on unlisted products
"""

import pytest
from src.product_search import search_product
from src.dynamic_catalog import synthesize_dynamic_product, infer_category, infer_brand


def test_infer_category_and_brand():
    assert infer_category("Dyson V12 Detect Slim") == "Home Appliances"
    assert infer_brand("Dyson V12 Detect Slim") == "Dyson"

    assert infer_category("PlayStation 5 Console") == "Gaming Consoles"
    assert infer_category("Kindle Paperwhite") in ["Consumer Electronics", "Displays & TVs", "Laptops"]


def test_synthesize_dynamic_product():
    prod = synthesize_dynamic_product("PlayStation 5 Disc Edition", user_price=44990.0)
    assert prod["name"] == "PlayStation 5 Disc Edition"
    assert prod["category"] == "Gaming Consoles"
    assert prod["current_price"] == 44990.0
    assert prod["is_dynamically_synthesized"] is True
    assert len(prod["market_prices"]) >= 3
    assert len(prod["reviews"]) >= 3


def test_search_product_unlisted_triggers_dynamic_synthesis():
    # An unlisted product should be dynamically generated
    res = search_product("GoPro Hero 12 Black", fallback_price=35000.0)
    assert res["found"] is True
    assert res["is_dynamic"] is True
    assert res["product"]["name"] == "GoPro Hero 12 Black"
    assert res["product"]["category"] == "Cameras & Drones"
