"""
Agent A: Many Small Tools Agent
Exposes 7 individual tools:
    1. search_product
    2. compare_prices
    3. find_discounts
    4. analyze_reviews
    5. find_alternatives
    6. compare_specs
    7. calculate_value_score

Tracks tool call sequences, execution durations, errors, completed steps, and loop guards.
Has NO access to "investigate_purchase".
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

from src.product_search import search_product
from src.price_analysis import compare_prices
from src.discount_analysis import find_discounts
from src.review_analysis import analyze_reviews
from src.alternatives import find_alternatives
from src.spec_comparison import compare_specs
from src.value_scoring import calculate_value_score

logger = logging.getLogger("realitycheck.many_tools_agent")


class ManyToolsAgent:
    """
    Agent exposed to seven fine-grained tools.
    Must orchestrate tool dependencies, validate inputs between steps,
    and prevent execution loops.
    """

    MAX_TOOL_CALLS = 10  # Loop prevention guard

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path
        self.tool_call_history: List[Dict[str, Any]] = []
        self.tool_errors: List[Dict[str, Any]] = []
        self.completed_steps: List[str] = []
        self.failed_steps: List[str] = []

    def _execute_tool(self, tool_name: str, func, *args, **kwargs) -> Any:
        """Executes a single tool with latency and error instrumentation."""
        step_start = time.perf_counter()
        call_record = {
            "step_index": len(self.tool_call_history) + 1,
            "tool_name": tool_name,
            "arguments": {
                "args": [str(a) if not isinstance(a, (int, float, str, bool)) else a for a in args],
                "kwargs": {k: (str(v) if not isinstance(v, (int, float, str, bool)) else v) for k, v in kwargs.items()}
            },
            "status": "RUNNING",
            "error": None
        }

        try:
            result = func(*args, **kwargs)
            duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
            call_record["duration_ms"] = duration_ms
            call_record["status"] = "SUCCESS"
            self.tool_call_history.append(call_record)
            self.completed_steps.append(tool_name)
            return result
        except Exception as e:
            duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
            call_record["duration_ms"] = duration_ms
            call_record["status"] = "FAILED"
            call_record["error"] = str(e)
            self.tool_call_history.append(call_record)
            self.tool_errors.append(call_record)
            self.failed_steps.append(tool_name)
            logger.error(f"Agent A: Tool '{tool_name}' failed: {e}")
            raise e

    def run(
        self,
        product_name: str,
        user_price: float,
        user_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates product investigation by independently selecting and invoking tools.
        """
        overall_start = time.perf_counter()
        self.tool_call_history = []
        self.tool_errors = []
        self.completed_steps = []
        self.failed_steps = []
        warnings = []
        confidence = 1.0

        # Step 1: Search Catalog
        if len(self.tool_call_history) >= self.MAX_TOOL_CALLS:
            return self._build_loop_limit_response(overall_start)

        search_res = self._execute_tool(
            "search_product",
            search_product,
            product_name,
            dataset_path=self.dataset_path,
            fallback_price=user_price
        )

        if not search_res.get("found") or not search_res.get("product"):
            elapsed_ms = round((time.perf_counter() - overall_start) * 1000, 2)
            return {
                "agent_name": "Many Tools Agent (Agent A)",
                "tool_calls_count": len(self.tool_call_history),
                "tool_call_sequence": self.tool_call_history,
                "tool_errors": self.tool_errors,
                "completed_steps": self.completed_steps,
                "failed_steps": self.failed_steps + ["product_not_found"],
                "total_execution_time_ms": elapsed_ms,
                "orchestration_overhead_ms": round(elapsed_ms - sum(c.get("duration_ms", 0) for c in self.tool_call_history), 2),
                "verdict": "AVOID",
                "value_score": 0,
                "confidence": 0.0,
                "report": {
                    "product": None,
                    "verdict": "AVOID",
                    "confidence": 0.0,
                    "verdict_reasoning": f"Product '{product_name}' not found.",
                    "warnings": [f"Catalog match failed for '{product_name}'."]
                }
            }

        product = search_res["product"]
        if search_res.get("match_confidence", 1.0) < 0.8:
            confidence -= 0.10
            warnings.append(f"Fuzzy match confidence: {search_res.get('match_confidence')*100:.0f}%")

        # Step 2: Compare Prices
        price_res = {}
        try:
            price_res = self._execute_tool(
                "compare_prices",
                compare_prices,
                product,
                user_price
            )
            if price_res.get("competitiveness_tier") == "UNKNOWN":
                confidence -= 0.25
                warnings.append("Market price benchmarks unavailable.")
        except Exception as e:
            warnings.append(f"Price comparison failed: {e}")
            confidence -= 0.20

        # Step 3: Find Discounts
        discount_res = {}
        try:
            discount_res = self._execute_tool(
                "find_discounts",
                find_discounts,
                product,
                base_price=user_price
            )
        except Exception as e:
            warnings.append(f"Discount lookup failed: {e}")
            confidence -= 0.10

        # Step 4: Analyze Reviews
        review_res = {}
        try:
            review_res = self._execute_tool(
                "analyze_reviews",
                analyze_reviews,
                product
            )
            if not review_res.get("is_data_sufficient"):
                confidence -= 0.25
                warnings.append("Insufficient customer reviews.")
            if review_res.get("warnings"):
                warnings.extend(review_res["warnings"])
        except Exception as e:
            warnings.append(f"Review analysis failed: {e}")
            confidence -= 0.20

        # Step 5: Find Alternatives
        alt_res = {}
        alternatives_list = []
        try:
            alt_res = self._execute_tool(
                "find_alternatives",
                find_alternatives,
                product,
                dataset_path=self.dataset_path,
                max_results=3
            )
            alternatives_list = alt_res.get("alternatives", [])
        except Exception as e:
            warnings.append(f"Alternative search failed: {e}")
            confidence -= 0.10

        # Step 6: Compare Specs
        spec_res = {}
        try:
            spec_res = self._execute_tool(
                "compare_specs",
                compare_specs,
                product,
                alternatives_list
            )
        except Exception as e:
            warnings.append(f"Spec comparison failed: {e}")
            confidence -= 0.10

        # Step 7: Calculate Value Score
        value_res = {}
        overall_score = 50
        try:
            pipeline_data = {
                "product": product,
                "price_analysis": price_res,
                "review_analysis": review_res,
                "spec_comparison": spec_res
            }
            value_res = self._execute_tool(
                "calculate_value_score",
                calculate_value_score,
                pipeline_data
            )
            overall_score = value_res.get("overall_score", 50)
        except Exception as e:
            warnings.append(f"Value scoring failed: {e}")
            confidence -= 0.20

        # Final Verdict Synthesis
        tier = price_res.get("competitiveness_tier", "UNKNOWN")
        lowest_market = price_res.get("lowest_market_price")
        review_neg_pct = review_res.get("sentiment_distribution", {}).get("negative", 0.0)

        if overall_score >= 75 and tier in ["EXCELLENT", "GOOD"]:
            verdict = "BUY"
            reasoning = (
                f"BUY recommended. High value score ({overall_score}/100) and user price ₹{user_price:,.2f} "
                f"is competitive against market low (₹{lowest_market:,.2f} if known)."
            )
        elif tier == "OVERPRICED" and lowest_market and user_price > lowest_market * 1.10:
            verdict = "WAIT"
            reasoning = (
                f"WAIT recommended. Marked price ₹{user_price:,.2f} is higher than available lowest "
                f"market price of ₹{lowest_market:,.2f}."
            )
        elif review_neg_pct >= 40.0 or overall_score < 50:
            verdict = "AVOID"
            reasoning = (
                f"AVOID recommended. Low value score ({overall_score}/100) or high negative feedback."
            )
        else:
            verdict = "WAIT"
            reasoning = f"WAIT recommended. Rated {overall_score}/100 with trade-offs."

        total_elapsed_ms = round((time.perf_counter() - overall_start) * 1000, 2)
        total_tool_duration_ms = sum(c.get("duration_ms", 0) for c in self.tool_call_history)
        orchestration_overhead_ms = round(max(0.0, total_elapsed_ms - total_tool_duration_ms), 2)
        confidence = max(0.20, min(1.0, round(confidence, 2)))

        report = {
            "product": product,
            "price_analysis": price_res,
            "discount_analysis": discount_res,
            "review_analysis": review_res,
            "alternatives": alternatives_list,
            "spec_comparison": spec_res,
            "value_score": overall_score,
            "value_score_details": value_res,
            "verdict": verdict,
            "confidence": confidence,
            "verdict_reasoning": reasoning,
            "warnings": warnings,
            "failed_steps": self.failed_steps,
            "completed_steps": self.completed_steps,
            "execution_time_ms": total_elapsed_ms,
            "data_source_type": "mock"
        }

        return {
            "agent_name": "Many Tools Agent (Agent A)",
            "tool_calls_count": len(self.tool_call_history),
            "tool_call_sequence": self.tool_call_history,
            "tool_errors": self.tool_errors,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "total_execution_time_ms": total_elapsed_ms,
            "total_tool_duration_ms": round(total_tool_duration_ms, 2),
            "orchestration_overhead_ms": orchestration_overhead_ms,
            "verdict": verdict,
            "value_score": overall_score,
            "confidence": confidence,
            "report": report
        }

    def _build_loop_limit_response(self, start_time: float) -> Dict[str, Any]:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "agent_name": "Many Tools Agent (Agent A)",
            "tool_calls_count": len(self.tool_call_history),
            "tool_call_sequence": self.tool_call_history,
            "tool_errors": [{"error": "Loop limit reached", "max_allowed": self.MAX_TOOL_CALLS}],
            "completed_steps": self.completed_steps,
            "failed_steps": ["loop_limit_exceeded"],
            "total_execution_time_ms": elapsed,
            "orchestration_overhead_ms": 0.0,
            "verdict": "AVOID",
            "value_score": 0,
            "confidence": 0.1,
            "report": {
                "product": None,
                "verdict": "AVOID",
                "confidence": 0.1,
                "verdict_reasoning": "Agent execution halted due to excessive loop count.",
                "warnings": ["Loop prevention guard triggered."]
            }
        }
