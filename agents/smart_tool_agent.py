"""
Agent B: One Smart Tool Agent
Exposes ONLY 1 high-level composed tool: "investigate_purchase"

Powered by Synapse Custom Mode Tool Composition.
Does NOT have access to individual component functions.
Eliminates intermediary multi-turn latency, parameter drift, and tool-chaining errors.
"""

import time
import logging
from typing import Dict, Any, Optional, List

from synapse.investigate_purchase_server import call_investigate_purchase_tool

logger = logging.getLogger("realitycheck.smart_tool_agent")


class SmartToolAgent:
    """
    Agent equipped with a single high-level composed MCP tool.
    Invokes 'investigate_purchase' in one deterministic call.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path
        self.tool_call_history: List[Dict[str, Any]] = []
        self.tool_errors: List[Dict[str, Any]] = []
        self.completed_steps: List[str] = []
        self.failed_steps: List[str] = []

    def run(
        self,
        product_name: str,
        user_price: float,
        user_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the product investigation using only the high-level composed tool.
        """
        overall_start = time.perf_counter()
        self.tool_call_history = []
        self.tool_errors = []
        self.completed_steps = []
        self.failed_steps = []

        step_start = time.perf_counter()
        call_record = {
            "step_index": 1,
            "tool_name": "investigate_purchase",
            "arguments": {
                "product_name": product_name,
                "user_price": user_price,
                "user_requirements": user_requirements
            },
            "status": "RUNNING",
            "error": None
        }

        try:
            report = call_investigate_purchase_tool(
                product_name=product_name,
                user_price=user_price,
                user_requirements=user_requirements
            )
            duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
            call_record["duration_ms"] = duration_ms
            call_record["status"] = "SUCCESS"
            self.tool_call_history.append(call_record)
            self.completed_steps.append("investigate_purchase")

            total_elapsed_ms = round((time.perf_counter() - overall_start) * 1000, 2)
            orchestration_overhead_ms = round(max(0.0, total_elapsed_ms - duration_ms), 2)

            return {
                "agent_name": "One Smart Tool Agent (Agent B)",
                "tool_calls_count": 1,
                "tool_call_sequence": self.tool_call_history,
                "tool_errors": [],
                "completed_steps": self.completed_steps,
                "failed_steps": report.get("failed_steps", []),
                "total_execution_time_ms": total_elapsed_ms,
                "total_tool_duration_ms": duration_ms,
                "orchestration_overhead_ms": orchestration_overhead_ms,
                "verdict": report.get("verdict", "WAIT"),
                "value_score": report.get("value_score", 0),
                "confidence": report.get("confidence", 0.0),
                "report": report
            }

        except Exception as e:
            duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
            call_record["duration_ms"] = duration_ms
            call_record["status"] = "FAILED"
            call_record["error"] = str(e)
            self.tool_call_history.append(call_record)
            self.tool_errors.append(call_record)
            self.failed_steps.append("investigate_purchase")
            total_elapsed_ms = round((time.perf_counter() - overall_start) * 1000, 2)

            logger.error(f"Agent B: investigate_purchase failed: {e}")
            return {
                "agent_name": "One Smart Tool Agent (Agent B)",
                "tool_calls_count": 1,
                "tool_call_sequence": self.tool_call_history,
                "tool_errors": self.tool_errors,
                "completed_steps": [],
                "failed_steps": ["investigate_purchase"],
                "total_execution_time_ms": total_elapsed_ms,
                "total_tool_duration_ms": duration_ms,
                "orchestration_overhead_ms": 0.0,
                "verdict": "AVOID",
                "value_score": 0,
                "confidence": 0.0,
                "report": {
                    "product": None,
                    "verdict": "AVOID",
                    "confidence": 0.0,
                    "verdict_reasoning": f"Tool error: {str(e)}",
                    "warnings": [str(e)]
                }
            }
