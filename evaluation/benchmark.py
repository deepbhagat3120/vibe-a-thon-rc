"""
Phase 7: RealityCheck Comparative Benchmark Module
Compares Agent A (Many Small Tools) vs Agent B (One Smart Tool)
across 5 deterministic test scenarios.

Metrics Evaluated:
    - Total execution time (ms)
    - Number of tool calls
    - Number of failed calls
    - Successful investigation steps
    - Workflow completeness rate (%)
    - Recommendation consistency
    - Orchestration overhead (ms)
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agents.many_tools_agent import ManyToolsAgent
from agents.smart_tool_agent import SmartToolAgent

logger = logging.getLogger("realitycheck.benchmark")

DEFAULT_TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")


def load_test_scenarios(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Loads standardized test cases from test_cases.json."""
    file_path = path or DEFAULT_TEST_CASES_PATH
    if not os.path.exists(file_path):
        logger.error(f"Test cases file not found at {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_benchmark(
    scenarios_path: Optional[str] = None,
    dataset_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes all scenarios across both Agent A and Agent B, collecting empirical performance metrics.

    Returns:
        Structured dictionary containing:
            - scenarios_count
            - results_per_scenario: detailed side-by-side run per scenario
            - summary_metrics: aggregate comparative stats
            - measurement_mode: 'ACTUAL_MEASURED'
    """
    scenarios = load_test_scenarios(scenarios_path)
    if not scenarios:
        return {"error": "No test scenarios loaded."}

    results = []

    # Initialize agents
    agent_a = ManyToolsAgent(dataset_path=dataset_path)
    agent_b = SmartToolAgent(dataset_path=dataset_path)

    # Accumulators for aggregate comparison
    a_total_time = 0.0
    b_total_time = 0.0
    a_total_tool_calls = 0
    b_total_tool_calls = 0
    a_failed_calls = 0
    b_failed_calls = 0
    a_total_steps_completed = 0
    b_total_steps_completed = 0
    consistent_verdicts_count = 0

    for scenario in scenarios:
        s_id = scenario["scenario_id"]
        title = scenario["title"]
        prod_name = scenario["product_name"]
        user_price = float(scenario["user_price"])
        reqs = scenario.get("user_requirements")

        # -------------------------------------------------------------
        # Execute Agent A (Many Small Tools)
        # -------------------------------------------------------------
        a_res = agent_a.run(product_name=prod_name, user_price=user_price, user_requirements=reqs)
        a_time = a_res.get("total_execution_time_ms", 0.0)
        a_calls = a_res.get("tool_calls_count", 0)
        a_fails = len(a_res.get("tool_errors", []))
        a_steps = len(a_res.get("completed_steps", []))
        a_verdict = a_res.get("verdict", "UNKNOWN")

        # -------------------------------------------------------------
        # Execute Agent B (One Smart Tool)
        # -------------------------------------------------------------
        b_res = agent_b.run(product_name=prod_name, user_price=user_price, user_requirements=reqs)
        b_time = b_res.get("total_execution_time_ms", 0.0)
        b_calls = b_res.get("tool_calls_count", 1)
        b_fails = len(b_res.get("tool_errors", []))
        # For Smart Tool, completed steps are internal steps completed by workflow
        b_internal_steps = b_res.get("report", {}).get("completed_steps", [])
        b_steps = len(b_internal_steps)
        b_verdict = b_res.get("verdict", "UNKNOWN")

        # Consistency check
        is_consistent = (a_verdict == b_verdict)
        if is_consistent:
            consistent_verdicts_count += 1

        # Accumulate
        a_total_time += a_time
        b_total_time += b_time
        a_total_tool_calls += a_calls
        b_total_tool_calls += b_calls
        a_failed_calls += a_fails
        b_failed_calls += b_fails
        a_total_steps_completed += a_steps
        b_total_steps_completed += b_steps

        # Calculate completeness (out of 7 core steps)
        a_completeness = round((a_steps / 7.0) * 100, 1)
        b_completeness = round((b_steps / 7.0) * 100, 1)

        results.append({
            "scenario_id": s_id,
            "title": title,
            "product_name": prod_name,
            "user_price": user_price,
            "agent_a": {
                "execution_time_ms": a_time,
                "tool_calls": a_calls,
                "failed_calls": a_fails,
                "completed_steps_count": a_steps,
                "completeness_pct": a_completeness,
                "verdict": a_verdict,
                "value_score": a_res.get("value_score"),
                "confidence": a_res.get("confidence")
            },
            "agent_b": {
                "execution_time_ms": b_time,
                "tool_calls": b_calls,
                "failed_calls": b_fails,
                "completed_steps_count": b_steps,
                "completeness_pct": b_completeness,
                "verdict": b_verdict,
                "value_score": b_res.get("value_score"),
                "confidence": b_res.get("confidence")
            },
            "verdict_consistent": is_consistent
        })

    num_scenarios = len(scenarios)
    avg_a_time = round(a_total_time / num_scenarios, 2)
    avg_b_time = round(b_total_time / num_scenarios, 2)
    time_reduction_pct = round(((avg_a_time - avg_b_time) / max(avg_a_time, 0.001)) * 100, 1)
    call_reduction_pct = round(((a_total_tool_calls - b_total_tool_calls) / max(a_total_tool_calls, 1)) * 100, 1)

    summary = {
        "num_scenarios": num_scenarios,
        "data_mode": "ACTUAL_MEASURED",
        "agent_a_many_tools": {
            "avg_execution_time_ms": avg_a_time,
            "total_tool_calls": a_total_tool_calls,
            "avg_tool_calls_per_run": round(a_total_tool_calls / num_scenarios, 1),
            "failed_calls": a_failed_calls,
            "total_completed_steps": a_total_steps_completed,
            "avg_completion_rate_pct": round((a_total_steps_completed / (num_scenarios * 7)) * 100, 1)
        },
        "agent_b_smart_tool": {
            "avg_execution_time_ms": avg_b_time,
            "total_tool_calls": b_total_tool_calls,
            "avg_tool_calls_per_run": round(b_total_tool_calls / num_scenarios, 1),
            "failed_calls": b_failed_calls,
            "total_completed_steps": b_total_steps_completed,
            "avg_completion_rate_pct": round((b_total_steps_completed / (num_scenarios * 7)) * 100, 1)
        },
        "comparison_highlights": {
            "tool_call_reduction_percent": call_reduction_pct,
            "latency_reduction_percent": time_reduction_pct,
            "recommendation_consistency_rate_pct": round((consistent_verdicts_count / num_scenarios) * 100, 1)
        }
    }

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "measurement_mode": "ACTUAL_MEASURED",
        "mock_dataset_notice": "DEMO MOCK DATASET - Metrics measured directly on local execution environment.",
        "summary": summary,
        "scenario_results": results
    }


def print_cli_benchmark():
    """Prints a clean tabular summary of benchmark results to console."""
    print("\n" + "=" * 80)
    print(" RealityCheck Hackathon Track 2 Benchmark: Many Tools vs. One Smart Tool")
    print("=" * 80)
    data = run_benchmark()
    summary = data["summary"]
    a = summary["agent_a_many_tools"]
    b = summary["agent_b_smart_tool"]
    h = summary["comparison_highlights"]

    print(f"\nScenarios Evaluated: {summary['num_scenarios']} | Mode: {data['measurement_mode']}")
    print("-" * 80)
    print(f"{'Metric':<35} | {'Agent A (Many Tools)':<20} | {'Agent B (One Smart Tool)':<20}")
    print("-" * 80)
    print(f"{'Total Tool Invocations':<35} | {a['total_tool_calls']:<20} | {b['total_tool_calls']:<20}")
    print(f"{'Avg Tool Invocations / Run':<35} | {a['avg_tool_calls_per_run']:<20} | {b['avg_tool_calls_per_run']:<20}")
    print(f"{'Average Latency (ms)':<35} | {a['avg_execution_time_ms']:<20} | {b['avg_execution_time_ms']:<20}")
    print(f"{'Failed Tool Calls':<35} | {a['failed_calls']:<20} | {b['failed_calls']:<20}")
    print(f"{'Workflow Completion Rate':<35} | {a['avg_completion_rate_pct']}%{'':<15} | {b['avg_completion_rate_pct']}%{'':<15}")
    print("-" * 80)
    print(f"Tool Call Complexity Reduction : {h['tool_call_reduction_percent']}% fewer tool calls")
    print(f"Recommendation Consistency     : {h['recommendation_consistency_rate_pct']}% exact agreement")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print_cli_benchmark()
