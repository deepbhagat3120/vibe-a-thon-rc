"""
Dynamic Catalog Synthesizer
Generates realistic, structured product benchmarks on-the-fly for any unlisted product.
Complies with hackathon rules by clearly identifying dynamically synthesized mock data.
"""

import re
import random
from typing import Dict, Any, Optional, List


def infer_category(query: str) -> str:
    """Infers product category from query text keywords."""
    q = query.lower()
    if any(k in q for k in ["headphone", "earphone", "earbud", "airpod", "tws", "buds", "anc", "audio", "headset"]):
        return "Headphones"
    elif any(k in q for k in ["phone", "mobile", "galaxy", "iphone", "pixel", "oneplus", "xiaomi", "realme", "redmi", "smartphone"]):
        return "Smartphones"
    elif any(k in q for k in ["laptop", "macbook", "zenbook", "thinkpad", "notebook", "chromebook", "ideapad"]):
        return "Laptops"
    elif any(k in q for k in ["watch", "band", "smartwatch", "fitbit", "garmin"]):
        return "Smartwatches"
    elif any(k in q for k in ["playstation", "ps5", "ps4", "xbox", "nintendo", "switch", "console"]):
        return "Gaming Consoles"
    elif any(k in q for k in ["vacuum", "cleaner", "dyson", "purifier", "microwave", "refrigerator", "fridge", "air conditioner"]):
        return "Home Appliances"
    elif any(k in q for k in ["tv", "television", "oled", "bravia", "qled", "monitor"]):
        return "Displays & TVs"
    elif any(k in q for k in ["speaker", "soundbar", "subwoofer", "alexa", "echo"]):
        return "Audio & Speakers"
    elif any(k in q for k in ["camera", "dslr", "mirrorless", "gopro", "drone"]):
        return "Cameras & Drones"
    return "Consumer Electronics"


def infer_brand(query: str) -> str:
    """Extracts known brand names or defaults to the first title-cased token."""
    known_brands = [
        "Apple", "Sony", "Samsung", "Google", "OnePlus", "JBL", "Bose", "boAt",
        "ASUS", "Lenovo", "Dell", "HP", "Acer", "Dyson", "Nintendo", "Microsoft",
        "Xiaomi", "Realme", "Nothing", "LG", "Panasonic", "Amazon", "Fitbit", "Garmin"
    ]
    for b in known_brands:
        if b.lower() in query.lower():
            return b
    tokens = query.strip().split()
    return tokens[0].capitalize() if tokens else "Generic"


def synthesize_dynamic_product(
    product_name: str,
    user_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Synthesizes a realistic, well-formed Product dictionary for any product query.

    Args:
        product_name: The user's query string (e.g. 'Dyson V12 Detect Slim' or 'PlayStation 5')
        user_price: User's offered or observed price (INR)

    Returns:
        Product dictionary compatible with all RealityCheck analysis functions.
    """
    clean_name = product_name.strip()
    category = infer_category(clean_name)
    brand = infer_brand(clean_name)
    
    # Establish realistic baseline price if not provided
    base_price = float(user_price) if (user_price and user_price > 0) else 15000.0
    mrp = round(base_price * 1.25, -2)

    # Market prices distributed realistically around base_price
    market_prices = [
        {"source": "Amazon India", "price": round(base_price * 0.94, -2), "in_stock": True},
        {"source": "Flipkart", "price": round(base_price * 0.98, -2), "in_stock": True},
        {"source": "Croma / Retail", "price": round(base_price * 1.05, -2), "in_stock": True},
        {"source": f"{brand} Official", "price": round(base_price * 1.10, -2), "in_stock": True}
    ]

    # Discounts
    bank_saving = min(round(base_price * 0.10, -2), 3000.0)
    discounts = [
        {
            "type": "bank",
            "description": f"Instant 10% discount on major bank credit cards (up to ₹{bank_saving:,.0f})",
            "amount": bank_saving,
            "code": "BANK10"
        },
        {
            "type": "coupon",
            "description": "Welcome promo coupon code",
            "amount": min(500.0, round(base_price * 0.03, -2)),
            "code": "FIRSTBUY"
        }
    ]

    # Category-specific templates for specs, pros, cons, and reviews
    if category == "Headphones":
        pros = ["Superior soundstage tuning", "Ergonomic comfort for long listening", "Reliable wireless connectivity"]
        cons = ["Carrying case sold separately", "Companion app requires frequent permissions"]
        recurring = ["Mild cushion warmth during prolonged outdoor sessions"]
        specs = {
            "battery_life_hours": 30,
            "noise_cancellation": "Active Noise Cancellation",
            "connectivity": "Bluetooth 5.3 + Aux",
            "weight_grams": 220,
            "warranty_months": 12
        }
    elif category == "Smartphones":
        pros = ["Vibrant high refresh rate display", "All-day dependable battery life", "Premium exterior build materials"]
        cons = ["Charging adapter omitted from retail packaging", "Pre-installed promotional applications"]
        recurring = ["Subtle warmth during intense 3D gaming or rapid charging"]
        specs = {
            "processor": f"Flagship Multi-Core {brand} Chipset",
            "display": "6.7-inch 120Hz HDR AMOLED Display",
            "battery_mah": 5000,
            "charging_watt": 67,
            "main_camera_mp": 50,
            "warranty_months": 12
        }
    elif category == "Laptops":
        pros = ["Fast multi-core compilation & multitasking", "Crisp high-resolution screen with thin bezels", "Solid hinge build"]
        cons = ["RAM soldered to motherboard (non-upgradable)", "Fan audible during sustained heavy loads"]
        recurring = ["Fingerprint smudges on chassis lid"]
        specs = {
            "processor": "High-Efficiency Multi-Core Processor",
            "ram": "16GB Fast LPDDR5 Memory",
            "storage": "512GB NVMe M.2 SSD",
            "battery_life_hours": 11,
            "weight_kg": 1.35,
            "warranty_months": 12
        }
    elif category == "Gaming Consoles":
        pros = ["Fast NVMe custom SSD eliminates loading screens", "Ray-tracing graphic fidelity at 60-120fps", "Superb tactile controller haptics"]
        cons = ["Bulky physical footprint on entertainment centers", "Proprietary internal expansion storage format"]
        recurring = ["Quickly depleted controller battery during rumble-heavy gameplay"]
        specs = {
            "cpu_gpu": "Custom 8-Core AMD Zen 2 + RDNA 2 Architecture",
            "storage": "1TB Custom High-Speed SSD",
            "resolution": "4K UHD at up to 120Hz with HDR",
            "warranty_months": 12
        }
    elif category == "Home Appliances":
        pros = ["Powerful suction and motor efficiency", "Washable HEPA filtration system", "Ergonomic handheld maneuverability"]
        cons = ["Battery life capped on maximum boost mode", "Replacement filter recurring cost"]
        recurring = ["Bin capacity requires frequent emptying in larger homes"]
        specs = {
            "motor_power_watts": 545,
            "battery_life_minutes": 60,
            "filtration": "Whole-machine HEPA filtration",
            "warranty_months": 24
        }
    else:
        pros = ["Solid industrial design and finish", "Meets contemporary performance standards", "Intuitive user interface"]
        cons = ["Higher initial retail price compared to budget tier", "Requires occasional firmware updates"]
        recurring = ["Occasional minor software sync hiccups"]
        specs = {
            "connectivity": "Wi-Fi & Bluetooth",
            "energy_rating": "5 Star High Efficiency",
            "warranty_months": 12
        }

    reviews = [
        {"rating": 5, "title": "Exceptional everyday performer", "comment": f"Bought this {clean_name} two weeks ago. Exceeded expectations in speed and build quality.", "sentiment": "positive"},
        {"rating": 4, "title": "Very satisfied with purchase", "comment": "Good value overall. Minor initial setup learning curve, but smooth sailing after.", "sentiment": "positive"},
        {"rating": 4, "title": "Solid premium hardware", "comment": f"Pleased with the hardware craftsmanship. {brand} delivered a dependable product.", "sentiment": "positive"},
        {"rating": 3, "title": "Decent, but priced on higher side", "comment": "Performs adequately, but wait for festival sales if you are looking for maximum discount.", "sentiment": "neutral"},
        {"rating": 2, "title": "Could improve ergonomics", "comment": f"Build quality is okay, but minor complaints about {cons[0].lower()}.", "sentiment": "negative"}
    ]

    slug = re.sub(r"[^a-z0-9]", "_", clean_name.lower())[:24]

    return {
        "id": f"prod_dynamic_{slug}",
        "brand": brand,
        "name": clean_name,
        "category": category,
        "mrp": mrp,
        "current_price": base_price,
        "market_prices": market_prices,
        "discounts": discounts,
        "rating": 4.3,
        "review_count": 2400,
        "reviews": reviews,
        "pros": pros,
        "cons": cons,
        "recurring_complaints": recurring,
        "specifications": specs,
        "alternatives": [],
        "is_mock": True,
        "is_dynamically_synthesized": True,
        "mock_notice": (
            "DYNAMICALLY SYNTHESIZED DEMO DATA — Product was not in the fixed local catalog, "
            "so RealityCheck synthesized realistic benchmark data based on your query and offered price."
        )
    }
