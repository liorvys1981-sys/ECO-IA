"""Dynamic pricing engine for ECO-IA services."""

from copy import deepcopy
import logging
from typing import Any

logger = logging.getLogger(__name__)


PLANS: dict[str, dict[str, Any]] = {
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

OVHCLOUD_US_IP_PRICING: dict[str, Any] = {
    "provider": "OVHcloud US",
    "region": "US",
    "currency": "USD",
    "prices_include_tax": False,
    "catalog_id": "GE-A8CCF",
    "last_modified": "2023-04-12",
    "created_at": "2021-07-27",
    "categories": {
        "dedicated_servers": [
            {"product": "Primary IPv4", "monthly_price_usd": 1.90},
            {"product": "Additional single IP", "monthly_price_usd": 1.90, "setup_price_usd": 6.00},
            {"product": "IP subnet /29", "usable_ip_addresses": 6, "monthly_price_usd": 16.00, "setup_price_usd": 39.00},
            {"product": "IP subnet /28", "usable_ip_addresses": 14, "monthly_price_usd": 31.00, "setup_price_usd": 67.00},
            {"product": "IP subnet /27", "usable_ip_addresses": 30, "monthly_price_usd": 61.00, "setup_price_usd": 121.00},
            {"product": "IP subnet /26", "usable_ip_addresses": 62, "monthly_price_usd": 121.00, "setup_price_usd": 221.00},
            {"product": "IP subnet /25", "usable_ip_addresses": 126, "monthly_price_usd": 242.00, "setup_price_usd": 299.00},
            {"product": "IP subnet /24", "usable_ip_addresses": 254, "monthly_price_usd": 484.00, "setup_price_usd": 732.00},
        ],
        "failover": [
            {"product": "Failover IP", "monthly_price_usd": 5.00, "setup_price_usd": 5.50},
            {"product": "Failover subnet /29", "monthly_price_usd": 25.00, "setup_price_usd": 39.00},
            {"product": "Failover subnet /28", "monthly_price_usd": 40.00, "setup_price_usd": 67.00},
            {"product": "Failover subnet /27", "monthly_price_usd": 70.00, "setup_price_usd": 121.00},
            {"product": "Failover subnet /26", "monthly_price_usd": 131.00, "setup_price_usd": 221.00},
            {"product": "Failover subnet /25", "monthly_price_usd": 251.00, "setup_price_usd": 410.00},
            {"product": "Failover subnet /24", "monthly_price_usd": 493.00, "setup_price_usd": 732.00},
            {"product": "Failover IPv6 subnet /64", "monthly_price_usd": 1.20, "setup_price_usd": 5.50},
            {
                "product": "Additional IPv6 subnet /56",
                "applies_to": "Dedicated servers",
                "one_time_setup_usd": 17.00,
                "notes": "Manual support request required.",
            },
        ],
        "colocation": [
            {"product": "Transfer subnet /30", "usable_ip_addresses": 2, "monthly_price_usd": 7.00, "setup_price_usd": 20.00},
            {"product": "IP subnet /29", "usable_ip_addresses": 5, "monthly_price_usd": 16.00, "setup_price_usd": 39.00},
            {"product": "IP subnet /28", "usable_ip_addresses": 13, "monthly_price_usd": 31.00, "setup_price_usd": 67.00},
            {"product": "IP subnet /27", "usable_ip_addresses": 29, "monthly_price_usd": 61.00, "setup_price_usd": 121.00},
            {"product": "IP subnet /26", "usable_ip_addresses": 61, "monthly_price_usd": 121.00, "setup_price_usd": 221.00},
            {"product": "IP subnet /25", "usable_ip_addresses": 125, "monthly_price_usd": 242.00, "setup_price_usd": 299.00},
            {"product": "IP subnet /24", "usable_ip_addresses": 253, "monthly_price_usd": 484.00, "setup_price_usd": 732.00},
        ],
        "managed_servers": [
            {"product": "Dedicated IPv4 address for SSL", "monthly_price_usd": 3.00, "setup_price_usd": 16.00},
        ],
        "web_hosting": [
            {"product": "Dedicated IPv4 address for SSL", "monthly_price_usd": 5.00, "setup_price_usd": 16.00},
        ],
        "vswitch_ipv4": [
            {"product": "IP subnet /29", "usable_ip_addresses": 5, "monthly_price_usd": 25.00, "setup_price_usd": 39.00},
            {"product": "IP subnet /28", "usable_ip_addresses": 13, "monthly_price_usd": 40.00, "setup_price_usd": 67.00},
            {"product": "IP subnet /27", "usable_ip_addresses": 29, "monthly_price_usd": 70.00, "setup_price_usd": 121.00},
            {"product": "IP subnet /26", "usable_ip_addresses": 61, "monthly_price_usd": 131.00, "setup_price_usd": 221.00},
            {"product": "IP subnet /25", "usable_ip_addresses": 125, "monthly_price_usd": 251.00, "setup_price_usd": 410.00},
            {"product": "IP subnet /24", "usable_ip_addresses": 253, "monthly_price_usd": 493.00, "setup_price_usd": 732.00},
        ],
        "vswitch_ipv6": [
            {
                "product": "IPv6 subnet /64",
                "usable_ip_addresses_note": "More than 18 quintillion IP addresses",
                "monthly_price_usd": 10.00,
            },
        ],
        "cloud": [
            {"product": "Floating IPv4", "monthly_price_usd": 3.50},
            {"product": "Floating IPv6", "monthly_price_usd": 1.50},
            {"product": "Primary IPv4", "monthly_price_usd": 0.60},
            {"product": "Primary IPv6", "monthly_price_usd": 0.00, "notes": "Free"},
        ],
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
        logger.debug(
            "Price for '%s': base=%.2f demand_factor=%.2f → %.2f",
            plan,
            base,
            demand_factor,
            price)
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

    def list_plans(self) -> list[dict[str, Any]]:
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

    def get_pricing_summary(self) -> dict[str, Any]:
        return {
            "demand_multiplier": self._demand_multiplier,
            "plans": self.list_plans(),
        }

    def get_ovhcloud_us_ip_pricing(self) -> dict[str, Any]:
        """Return the OVHcloud US IP pricing catalog in USD."""
        return deepcopy(OVHCLOUD_US_IP_PRICING)
