"""Monetization agent wrapper."""

from typing import Any

from core.agent_base import AgentBase

from .billing import BillingManager
from .clients import ClientManager
from .pricing import PricingEngine


class MonetizationAgent(AgentBase):
    supported_task_types = (
        "billing_task",
        "create_client",
        "list_clients",
        "list_ip_pricing",
        "upgrade_plan",
        "get_price",
        "list_plans",
        "create_invoice",
        "check_failed_payments",
        "detect_upsell_opportunities",
        "payment_succeeded",
        "payment_failed",
    )

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

        if task_type == "list_ip_pricing":
            return self.pricing_engine.get_ovhcloud_us_ip_pricing()

        if task_type == "create_invoice":
            invoice = await self.billing_manager.create_invoice(
                task["customer_id"],
                task["amount_cents"],
                task["description"],
            )
            return {"status": "created", "invoice": invoice}

        if task_type == "check_failed_payments":
            invoices = await self.billing_manager.list_invoices()
            failed = [
                invoice
                for invoice in invoices
                if invoice.get("status") == "failed"
                or invoice.get("params", {}).get("status") == "failed"
            ]
            return {"checked": len(invoices), "failed_invoices": failed}

        if task_type == "detect_upsell_opportunities":
            return {"opportunities": self.client_manager.detect_upsell_opportunities()}

        if task_type == "payment_succeeded":
            invoice_id = task.get("invoice_id", "unknown")
            return {"status": "processed", "action": "payment_recorded", "invoice_id": invoice_id}

        if task_type == "payment_failed":
            invoice_id = task.get("invoice_id", "unknown")
            return {"status": "processed", "action": "payment_failed", "invoice_id": invoice_id}

        if task_type == "summary":
            overdue_invoices = await self._get_overdue_invoices()
            dynamic_pricing = await self._update_dynamic_pricing()
            return {
                "overdue_invoices": overdue_invoices,
                "dynamic_pricing": dynamic_pricing,
                "revenue_summary": self.billing_manager.get_revenue_summary(),
            }

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}

    async def _update_dynamic_pricing(self) -> dict[str, Any]:
        active_clients = self.client_manager.get_summary().get("active_clients", 0)
        multiplier = 1.2 if active_clients > 10 else 1.0
        self.pricing_engine.set_demand_multiplier(multiplier)
        return {"multiplier": float(multiplier)}

    async def _get_overdue_invoices(self) -> list[dict[str, Any]]:
        invoices = await self.billing_manager.list_invoices()
        return [
            invoice
            for invoice in invoices
            if invoice.get("status") == "overdue"
            or invoice.get("params", {}).get("status") == "overdue"
        ]

    async def create_invoice(
        self,
        customer_id: str,
        amount_usd: float,
        description: str,
    ) -> dict[str, Any]:
        invoice = await self.billing_manager.create_invoice(
            customer_id,
            int(round(amount_usd * 100)),
            description,
        )
        return {
            "status": "created",
            "customer_id": customer_id,
            "invoice": invoice,
        }
