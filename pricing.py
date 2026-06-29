"""Dynamic pricing engine for ECO-IA services."""

import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


PLANS: Dict[str, Dict[str, Any]] = {
    "basic": {
        "name": "Basic",
        "base_price_usd": 9.99,
        "api_calls_per_month": 10_000,
        "storage_gb": 10,
        "support": "community",
    },
    "pro": {
        "name": "Pro",
        "base_price_usd": 49.99,
        "api_calls_per_month": 100_000,
        "storage_gb": 100,
        "support": "email",
    },
    "enterprise": {
        "name": "Enterprise",
        "base_price_usd": 199.99,
        "api_calls_per_month": 1_000_000,
        "storage_gb": 1_000,
        "support": "dedicated",
    },
}


class PricingEngine:
    """Computes dynamic pricing based on demand and resource usage."""

    def __init__(self, demand_multiplier: float = 1.0) -> None:
        self._demand_multiplier = demand_multiplier
        self._plans = dict(PLANS)

    # ------------------------------------------------------------------
    # Price calculation
    # ------------------------------------------------------------------

    def get_price(self, plan: str, usage_pct: float = 0.0) -> float:
        """Calculate the current price for *plan* considering demand.

        Args:
            plan: Plan name ("basic", "pro", "enterprise").
            usage_pct: Current server utilisation percentage (0–100).

        Returns:
            Adjusted price in USD.
        """
        plan_config = self._plans.get(plan)
        if plan_config is None:
            raise ValueError(f"Unknown plan: {plan!r}")

        base = plan_config["base_price_usd"]
        demand_factor = self._compute_demand_factor(usage_pct)
        price = round(base * self._demand_multiplier * demand_factor, 2)
        logger.debug("Price for '%s': base=%.2f demand_factor=%.2f → %.2f", plan, base, demand_factor, price)
        return price

    def _compute_demand_factor(self, usage_pct: float) -> float:
        """Return a multiplier based on server utilisation."""
        if usage_pct < 50:
            return 1.0          # normal pricing
        if usage_pct < 75:
            return 1.1          # slight surge
        if usage_pct < 90:
            return 1.25         # surge pricing
        return 1.5              # peak pricing

    # ------------------------------------------------------------------
    # Plan management
    # ------------------------------------------------------------------

    def list_plans(self) -> List[Dict[str, Any]]:
        """Return all available plans with current prices."""
        return [
            {**v, "plan_key": k, "current_price_usd": self.get_price(k)}
            for k, v in self._plans.items()
        ]

    def recommend_plan(self, monthly_api_calls: int, storage_gb: int) -> str:
        """Recommend the cheapest plan that covers the given requirements."""
        for plan_key in ("basic", "pro", "enterprise"):
            plan = self._plans[plan_key]
            if (
                plan["api_calls_per_month"] >= monthly_api_calls
                and plan["storage_gb"] >= storage_gb
            ):
                return plan_key
        return "enterprise"

    def set_demand_multiplier(self, multiplier: float) -> None:
        """Override the global demand multiplier (1.0 = normal)."""
        if multiplier <= 0:
            raise ValueError("Demand multiplier must be positive.")
        self._demand_multiplier = multiplier
        logger.info("Demand multiplier set to %.2f", multiplier)

    def get_pricing_summary(self) -> Dict[str, Any]:
        return {
            "demand_multiplier": self._demand_multiplier,
            "plans": self.list_plans(),
        }
