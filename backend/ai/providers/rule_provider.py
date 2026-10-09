from backend.ai.providers.base_provider import AIProvider


class RuleBasedProvider(AIProvider):

    def generate(
        self,
        context: dict,
    ) -> str:

        decisions = context.get("decisions", [])
        risk_level = context.get(
            "risk_level",
            "unknown",
        )

        if not decisions:
            return (
                "Current supply-chain conditions are "
                "within the configured operating limits."
            )

        primary = decisions[0]

        return (
            f"Overall risk is {risk_level}. "
            f"The primary recommended action is "
            f"{primary['action']}. "
            f"Reason: {primary['reason']}"
        )
