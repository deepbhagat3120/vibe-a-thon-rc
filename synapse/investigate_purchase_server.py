"""
Synapse Custom Mode Composed MCP Tool Server
Exposes a single high-level tool: "investigate_purchase"

Generated via Synapse Custom Mode Tool Composition.
Internally orchestrates:
    - search_product
    - compare_prices
    - find_discounts
    - analyze_reviews
    - find_alternatives
    - compare_specs
    - calculate_value_score
"""

import sys
import json
import logging
from typing import Optional, Dict, Any

from mcp.server.mcpserver import MCPServer
from src.purchase_workflow import investigate_purchase

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("realitycheck.synapse_server")

# Initialize MCP Server for Synapse
server = MCPServer(
    name="RealityCheck-InvestigatePurchase",
    description="Synapse Custom Mode Composed MCP Server for Comprehensive Purchasing Decisions",
    version="1.0.0"
)


@server.tool(
    name="investigate_purchase",
    description=(
        "Comprehensive purchasing investigation tool composed from 7 specialized functions. "
        "Evaluates product pricing across retailers, detects applicable coupon/bank discounts, "
        "analyzes real customer review sentiments and recurring defects, surfaces competing alternatives, "
        "compares hardware specifications, calculates a deterministic 0-100 value-for-money score, "
        "and delivers an evidence-based BUY / WAIT / AVOID recommendation."
    )
)
def investigate_purchase_mcp_tool(
    product_name: str,
    user_price: float,
    user_requirements: str = ""
) -> str:
    """
    Synapse Composed Tool:
    Args:
        product_name: The name or model string of the product to analyze (e.g. 'Sony WH-CH720N').
        user_price: The price offered to or considered by the user (INR).
        user_requirements: Optional specific constraints or priorities (e.g. 'battery life', 'travel').
    Returns:
        JSON string containing the complete investigation report and BUY/WAIT/AVOID verdict.
    """
    logger.info(f"Synapse MCP Tool 'investigate_purchase' called for '{product_name}' @ ₹{user_price}")
    result = investigate_purchase(
        product_name=product_name,
        user_price=user_price,
        user_requirements=user_requirements if user_requirements else None
    )
    return json.dumps(result, indent=2, default=str)


def call_investigate_purchase_tool(
    product_name: str,
    user_price: float,
    user_requirements: Optional[str] = None
) -> Dict[str, Any]:
    """
    Direct Python programmatic interface to the composed Synapse MCP tool.
    Used by Smart Tool Agent to invoke the tool directly or over transport.
    """
    return investigate_purchase(
        product_name=product_name,
        user_price=user_price,
        user_requirements=user_requirements
    )


if __name__ == "__main__":
    logger.info("Starting RealityCheck Synapse MCP Server on STDIO transport...")
    server.run(transport="stdio")
