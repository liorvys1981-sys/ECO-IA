"""Monetization agent wrapper."""

from typing import Any

from core.agent_base import AgentBase

from .billing import BillingManager
from .clients import ClientManager
from .pricing import PricingEngine


class MonetizationAgent(AgentBase):
    def __init__(
        self,
        message_bus=None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name="monetization",
            description="Client management, billing, and dynamic pricing",
            message_bus=message_bus,
            config=config,
        )
        self.pricing_engine = PricingEngine(
            demand_multiplier=self.get_config("pricing", {}).get("demand_multiplier", 1.0)
        )
        self.client_manager = ClientManager()
        self.billing_manager = BillingManager()

    async def on_start(self) -> None:
        return None

    async def on_stop(self) -> None:
        return None

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        task_type = task.get("type", "summary")

        if task_type == "create_client":
            client = self.client_manager.create_client(
                task["name"],
                task["email"],
                task.get("plan", "basic"),
                task.get("stripe_customer_id"),
            )
            self.tasks_completed += 1
            return {"status": "created", "client": client.to_dict()}

        if task_type == "list_clients":
            clients = [client.to_dict() for client in self.client_manager.list_clients()]
            return {"clients": clients, "total": len(clients)}

        if task_type == "upgrade_plan":
            updated = self.client_manager.upgrade_plan(task["client_id"], task["new_plan"])
            return {"status": "updated" if updated else "not_found"}

        if task_type == "get_price":
            price = self.pricing_engine.get_price(task["plan"], task.get("usage_pct", 0.0))
            return {
                "plan": task["plan"],
                "price_usd": price,
            }

        if task_type == "list_plans":
            return {"plans": self.pricing_engine.list_plans()}

        if task_type == "create_invoice":
            invoice = await self.billing_manager.create_invoice(
                task["customer_id"],
                task["amount_cents"],
                task["description"],
            )
            return {"status": "created", "invoice": invoice}

        if task_type == "summary":
            return {
                "clients": self.client_manager.get_summary(),
                "pricing": self.pricing_engine.get_pricing_summary(),
                "billing": self.billing_manager.get_revenue_summary(),
            }

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}
