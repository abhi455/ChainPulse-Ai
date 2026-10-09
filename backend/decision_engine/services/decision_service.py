from backend.decision_engine.metrics import risk_level, risk_score
from backend.decision_engine.rules import (
    evaluate_inventory,
    evaluate_overstock,
    evaluate_supplier,
)


class DecisionService:

    @staticmethod
    def evaluate(
        current_inventory: float,
        reorder_point: float,
        stockout_risk: str,
        overstock_risk: str,
        supplier_risk_level: str,
    ) -> dict:

        if current_inventory < 0:
            raise ValueError(
                "current_inventory cannot be negative"
            )

        if reorder_point < 0:
            raise ValueError(
                "reorder_point cannot be negative"
            )

        valid_risks = {
            "low",
            "medium",
            "high",
            "critical",
        }

        for value in (
            stockout_risk,
            overstock_risk,
            supplier_risk_level,
        ):
            if value not in valid_risks:
                raise ValueError(
                    f"Invalid risk level: {value}"
                )

        decisions = []

        inventory_decision = evaluate_inventory(
            current_inventory=current_inventory,
            reorder_point=reorder_point,
            stockout_risk=stockout_risk,
        )

        if inventory_decision:
            decisions.append(inventory_decision)

        supplier_decision = evaluate_supplier(
            supplier_risk_level=supplier_risk_level,
        )

        if supplier_decision:
            decisions.append(supplier_decision)

        overstock_decision = evaluate_overstock(
            overstock_risk=overstock_risk,
        )

        if overstock_decision:
            decisions.append(overstock_decision)

        score = risk_score(
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk,
            supplier_risk=supplier_risk_level,
        )

        overall_risk = risk_level(score)

        if not decisions:
            decisions.append(
                {
                    "action": "NO_ACTION_REQUIRED",
                    "priority": "low",
                    "reason": "Current supply-chain conditions are within acceptable limits.",
                    "confidence": 90.0,
                    "category": "general",
                }
            )

        normalized_decisions = []

        for decision in decisions:
            if isinstance(decision, dict):
                normalized_decisions.append(decision)
            else:
                normalized_decisions.append(
                    {
                        "action": decision.action,
                        "priority": decision.priority,
                        "reason": decision.reason,
                        "confidence": decision.confidence,
                        "category": decision.category,
                    }
                )

        priority_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
        }

        normalized_decisions.sort(
            key=lambda item: priority_order[item["priority"]]
        )

        return {
            "risk_score": score,
            "risk_level": overall_risk,
            "decisions": normalized_decisions,
        }
