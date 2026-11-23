"""
Function 6: Specification Comparison
Generates side-by-side comparison matrix for key specs across the target product and alternatives.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("realitycheck.spec_comparison")


def compare_specs(product: Dict[str, Any], alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compares key specifications between the subject product and its alternatives.

    Attributes evaluated (category-tailored):
    - Headphones: Battery Life, ANC, Weight, Connectivity, Warranty
    - Smartphones: Processor, Display, Battery/Charging, Cameras, Weight
    - Laptops: Processor, RAM/Storage, Display, Battery, Weight
    - Smartwatches: Display, Battery, Water Resistance, Sensors

    Args:
        product: Target product dict.
        alternatives: List of alternative product dicts.

    Returns:
        Structured specification comparison matrix and summary.
    """
    if not isinstance(product, dict) or not product:
        return {
            "success": False,
            "error": "Invalid target product data.",
            "target_product_name": "",
            "compared_attributes": [],
            "spec_matrix": {},
            "key_strengths": [],
            "key_tradeoffs": []
        }

    target_name = product.get("name", "Target Product")
    target_specs = product.get("specifications", {})
    target_price = float(product.get("current_price", 0) or product.get("mrp", 0))
    category = product.get("category", "")

    # Define relevant attributes by category
    category_attr_keys = {
        "Headphones": ["battery_life_hours", "noise_cancellation", "weight_grams", "connectivity", "warranty_months"],
        "Smartphones": ["processor", "display", "battery_mah", "charging_watt", "main_camera_mp", "warranty_months"],
        "Laptops": ["processor", "ram", "storage", "display", "battery_life_hours", "weight_kg"],
        "Smartwatches": ["display", "battery_life_hours", "water_resistance", "sensors", "os_compatibility"]
    }

    selected_attrs = category_attr_keys.get(category)
    if not selected_attrs:
        # Generic fallback
        selected_attrs = list(target_specs.keys())[:5]

    # Build spec matrix
    matrix: Dict[str, Dict[str, Any]] = {}
    
    # Add Price row
    matrix["Price (₹)"] = {
        target_name: f"₹{target_price:,.0f}"
    }
    for alt in alternatives:
        a_name = alt.get("name", "Alt")
        a_price = float(alt.get("price", 0))
        matrix["Price (₹)"][a_name] = f"₹{a_price:,.0f}"

    # Add Specification rows
    readable_names = {
        "battery_life_hours": "Battery Life",
        "noise_cancellation": "Noise Cancellation",
        "weight_grams": "Weight",
        "connectivity": "Connectivity",
        "warranty_months": "Warranty",
        "processor": "Processor / CPU",
        "display": "Display",
        "ram_rom": "RAM / Storage",
        "battery_mah": "Battery Capacity",
        "charging_watt": "Charging Speed",
        "main_camera_mp": "Main Camera",
        "ram": "RAM Memory",
        "storage": "Storage Drive",
        "weight_kg": "Weight",
        "water_resistance": "Water Resistance",
        "sensors": "Health Sensors",
        "os_compatibility": "OS Compatibility"
    }

    def format_val(key: str, val: Any) -> str:
        if val is None or val == "":
            return "N/A"
        if key == "battery_life_hours":
            return f"{val} hours"
        if key == "weight_grams":
            return f"{val} g"
        if key == "weight_kg":
            return f"{val} kg"
        if key == "warranty_months":
            return f"{val} months"
        if key == "battery_mah":
            return f"{val} mAh"
        if key == "charging_watt":
            return f"{val}W fast charge"
        if key == "main_camera_mp":
            return f"{val} MP"
        return str(val)

    for attr in selected_attrs:
        row_title = readable_names.get(attr, attr.replace("_", " ").title())
        matrix[row_title] = {
            target_name: format_val(attr, target_specs.get(attr))
        }
        for alt in alternatives:
            a_name = alt.get("name", "Alt")
            alt_specs = alt.get("specifications", {})
            matrix[row_title][a_name] = format_val(attr, alt_specs.get(attr))

    # Determine key strengths and trade-offs
    strengths = []
    tradeoffs = []

    # Battery comparison
    t_battery = target_specs.get("battery_life_hours")
    if t_battery:
        better_count = 0
        worse_count = 0
        for alt in alternatives:
            a_bat = alt.get("specifications", {}).get("battery_life_hours")
            if a_bat:
                if t_battery >= a_bat:
                    better_count += 1
                else:
                    worse_count += 1
        if better_count > 0 and worse_count == 0:
            strengths.append(f"Longer battery life ({t_battery} hrs) than compared alternatives.")
        elif worse_count > 0 and better_count == 0:
            tradeoffs.append(f"Lower battery duration ({t_battery} hrs) compared to competing models.")

    # Weight comparison
    t_weight = target_specs.get("weight_grams")
    if t_weight:
        if all(t_weight <= alt.get("specifications", {}).get("weight_grams", 9999) for alt in alternatives if alt.get("specifications", {}).get("weight_grams")):
            strengths.append(f"Lightweight build ({t_weight}g) for fatigue-free extended usage.")

    # Price vs alternatives
    alt_prices = [float(a.get("price", 0)) for a in alternatives if float(a.get("price", 0)) > 0]
    if alt_prices:
        avg_alt_price = sum(alt_prices) / len(alt_prices)
        if target_price < avg_alt_price * 0.85:
            strengths.append(f"Priced ₹{avg_alt_price - target_price:,.0f} lower than average peer cost.")
        elif target_price > avg_alt_price * 1.25:
            tradeoffs.append(f"Priced ₹{target_price - avg_alt_price:,.0f} higher than typical segment alternatives.")

    return {
        "success": True,
        "target_product_name": target_name,
        "category": category,
        "compared_attributes": list(matrix.keys()),
        "spec_matrix": matrix,
        "key_strengths": strengths or ["Balanced feature configuration across category baseline."],
        "key_tradeoffs": tradeoffs or ["No major deal-breaking specification disadvantages."]
    }
