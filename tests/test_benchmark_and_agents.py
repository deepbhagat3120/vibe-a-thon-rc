"""
Tests for Benchmark and Agents execution
"""

import pytest
from agents.many_tools_agent import ManyToolsAgent
from agents.smart_tool_agent import SmartToolAgent
from evaluation.benchmark import run_benchmark


def test_many_tools_agent_execution():
    agent = ManyToolsAgent()
    res = agent.run("Sony WH-CH720N", 8999.0)
    assert res["agent_name"] == "Many Tools Agent (Agent A)"
    assert res["tool_calls_count"] == 7
    assert len(res["completed_steps"]) == 7
    assert res["verdict"] in ["BUY", "WAIT"]
    assert res["value_score"] > 0


def test_smart_tool_agent_execution():
    agent = SmartToolAgent()
    res = agent.run("Sony WH-CH720N", 8999.0)
    assert res["agent_name"] == "One Smart Tool Agent (Agent B)"
    assert res["tool_calls_count"] == 1
    assert "investigate_purchase" in res["completed_steps"]
    assert res["verdict"] in ["BUY", "WAIT"]


def test_run_benchmark():
    bench = run_benchmark()
    assert bench["measurement_mode"] == "ACTUAL_MEASURED"
    summary = bench["summary"]
    assert summary["num_scenarios"] == 5
    assert summary["agent_a_many_tools"]["total_tool_calls"] == 35
    assert summary["agent_b_smart_tool"]["total_tool_calls"] == 5
    assert summary["comparison_highlights"]["tool_call_reduction_percent"] > 80.0
