"""
Safety and Confirmation Module
Enforces explicit user confirmation before executing state-changing actions.
Architecture: PREPARE ACTION -> DISPLAY ACTION -> USER CONFIRMATION -> EXECUTE
"""

import logging
from typing import Dict, Any, Optional, Literal

logger = logging.getLogger("realitycheck.safety")

ActionType = Literal["CREATE_PRICE_ALERT", "ADD_TO_WISHLIST", "ADD_TO_CART", "PURCHASE"]


class SafetyConfirmationManager:
    """
    Manages action preparation, user authorization checks, and guarded execution.
    Guarantees no state-modifying action executes without verified user confirmation.
    """

    def __init__(self):
        self._action_registry: Dict[str, Dict[str, Any]] = {}

    def prepare_action(
        self,
        action_type: ActionType,
        product_id: str,
        product_name: str,
        target_price: Optional[float] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stage 1: Prepares the action and constructs a detailed confirmation card for the user.
        """
        import uuid
        action_id = f"act_{uuid.uuid4().hex[:8]}"

        if action_type == "CREATE_PRICE_ALERT":
            msg = (
                f"Confirm creating a price drop alert for '{product_name}' "
                f"when price reaches ₹{target_price:,.2f}?"
                if target_price else f"Confirm creating a price drop alert for '{product_name}'?"
            )
        elif action_type == "ADD_TO_WISHLIST":
            msg = f"Confirm saving '{product_name}' to your saved wishlist?"
        elif action_type == "ADD_TO_CART":
            msg = f"Confirm staging '{product_name}' in external cart?"
        elif action_type == "PURCHASE":
            msg = (
                f"[CRITICAL SAFETY GUARD] Direct purchases are disabled in this MVP. "
                f"Purchase execution requires manual external merchant checkout."
            )
        else:
            msg = f"Confirm execution of action {action_type} for '{product_name}'?"

        action_record = {
            "action_id": action_id,
            "action_type": action_type,
            "product_id": product_id,
            "product_name": product_name,
            "target_price": target_price,
            "parameters": extra_params or {},
            "status": "PREPARED",
            "requires_confirmation": True,
            "user_confirmed": None,
            "confirmation_message": msg,
            "can_execute": False
        }

        self._action_registry[action_id] = action_record
        logger.info(f"Action prepared: {action_id} ({action_type})")
        return action_record

    def submit_user_decision(self, action_id: str, confirmed: bool) -> Dict[str, Any]:
        """
        Stage 2 & 3: Records the user's explicit consent or rejection.
        """
        if action_id not in self._action_registry:
            return {
                "success": False,
                "error": f"Action ID '{action_id}' not found.",
                "status": "ERROR"
            }

        action = self._action_registry[action_id]
        if confirmed:
            action["user_confirmed"] = True
            action["status"] = "CONFIRMED"
            action["can_execute"] = True
            logger.info(f"User APPROVED action {action_id}")
        else:
            action["user_confirmed"] = False
            action["status"] = "REJECTED"
            action["can_execute"] = False
            logger.info(f"User DECLINED action {action_id}")

        return action

    def execute_action(self, action_id: str) -> Dict[str, Any]:
        """
        Stage 4: Executes the action ONLY IF user_confirmed is True.
        Rejects execution otherwise.
        """
        if action_id not in self._action_registry:
            return {
                "success": False,
                "error": f"Action ID '{action_id}' does not exist.",
                "status": "FAILED"
            }

        action = self._action_registry[action_id]

        # Enforce Safety Guard
        if not action.get("user_confirmed"):
            logger.warning(f"BLOCKED unauthorized execution attempt for action {action_id} (status: {action.get('status')})")
            return {
                "success": False,
                "error": "SAFETY VIOLATION: Action cannot be executed without explicit user confirmation.",
                "status": action.get("status", "REJECTED"),
                "action_id": action_id
            }

        action_type = action.get("action_type")
        product_name = action.get("product_name")

        if action_type == "PURCHASE":
            return {
                "success": False,
                "error": "Direct autonomous purchasing is strictly prohibited in RealityCheck MVP.",
                "status": "BLOCKED_BY_POLICY",
                "action_id": action_id
            }

        # Simulated execution of safe consumer actions (e.g., alert or wishlist)
        action["status"] = "EXECUTED"
        action["execution_result"] = f"Successfully executed {action_type} for '{product_name}'."
        logger.info(f"Successfully executed action {action_id}")

        return {
            "success": True,
            "status": "EXECUTED",
            "message": action["execution_result"],
            "action_id": action_id,
            "action_type": action_type
        }


# Global singleton instance
safety_manager = SafetyConfirmationManager()
