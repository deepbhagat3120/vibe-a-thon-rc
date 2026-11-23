"""
Tests for SafetyConfirmationManager
"""

import pytest
from src.safety import SafetyConfirmationManager


def test_safety_lifecycle_confirmed():
    manager = SafetyConfirmationManager()
    
    # 1. Prepare
    action = manager.prepare_action(
        action_type="CREATE_PRICE_ALERT",
        product_id="prod_sony_wh_ch720n",
        product_name="Sony WH-CH720N",
        target_price=7999.0
    )
    action_id = action["action_id"]
    assert action["status"] == "PREPARED"
    assert action["requires_confirmation"] is True

    # 2. Try executing BEFORE confirmation -> Must be BLOCKED
    exec_attempt = manager.execute_action(action_id)
    assert exec_attempt["success"] is False
    assert "SAFETY VIOLATION" in exec_attempt["error"]

    # 3. User Confirms
    decision = manager.submit_user_decision(action_id, confirmed=True)
    assert decision["status"] == "CONFIRMED"
    assert decision["user_confirmed"] is True

    # 4. Execute After Confirmation -> Must Succeed
    exec_success = manager.execute_action(action_id)
    assert exec_success["success"] is True
    assert exec_success["status"] == "EXECUTED"


def test_safety_lifecycle_rejected():
    manager = SafetyConfirmationManager()
    action = manager.prepare_action(
        action_type="ADD_TO_WISHLIST",
        product_id="prod_macbook_air_m2",
        product_name="Apple MacBook Air M2"
    )
    action_id = action["action_id"]

    # User Rejects
    decision = manager.submit_user_decision(action_id, confirmed=False)
    assert decision["status"] == "REJECTED"
    assert decision["user_confirmed"] is False

    # Attempt Execution -> Must be BLOCKED
    exec_attempt = manager.execute_action(action_id)
    assert exec_attempt["success"] is False
    assert "SAFETY VIOLATION" in exec_attempt["error"]


def test_safety_blocks_direct_purchases():
    manager = SafetyConfirmationManager()
    action = manager.prepare_action(
        action_type="PURCHASE",
        product_id="prod_oneplus_12r",
        product_name="OnePlus 12R",
        target_price=39999.0
    )
    action_id = action["action_id"]
    manager.submit_user_decision(action_id, confirmed=True)

    # Even if confirmed, direct autonomous purchase must be blocked by policy in MVP
    result = manager.execute_action(action_id)
    assert result["success"] is False
    assert result["status"] == "BLOCKED_BY_POLICY"
