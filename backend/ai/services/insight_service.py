from backend.ai.models import AIInsight
from backend.ai.providers import AIProvider, RuleBasedProvider


class InsightService:

    def __init__(
        self,
        provider: AIProvider | None = None,
    ) -> None:
        self.provider = provider or RuleBasedProvider()

    def explain_decision(
        self,
        decision_result: dict,
    ) -> AIInsight:

        if not isinstance(decision_result, dict):
            raise ValueError(
                "decision_result must be a dictionary"
            )

        risk_level = decision_result.get(
            "risk_level",
            "unknown",
        )

        decisions = decision_result.get(
            "decisions",
            [],
        )

        if not isinstance(decisions, list):
            raise ValueError(
                "decisions must be a list"
            )

        context = {
            "risk_level": risk_level,
            "decisions": decisions,
        }

        explanation = self.provider.generate(
            context
        )

        if decisions:
            primary = decisions[0]

            confidence = float(
                primary.get(
                    "confidence",
                    50.0,
                )
            )

            category = primary.get(
                "category",
                "general",
            )

            recommendation = primary.get(
                "action",
                "NO_ACTION_REQUIRED",
            )

        else:
            confidence = 90.0
            category = "general"
            recommendation = "NO_ACTION_REQUIRED"

        return AIInsight(
            title="ChainPulse Supply Chain Insight",
            summary=explanation,
            recommendation=recommendation,
            confidence=confidence,
            category=category,
        )
