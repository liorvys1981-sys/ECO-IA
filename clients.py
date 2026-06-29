"""Client management for the monetization agent."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class Client:
    """Represents a paying client of the ECO-IA system."""

    def __init__(
        self,
        client_id: str,
        name: str,
        email: str,
        plan: str = "basic",
        stripe_customer_id: Optional[str] = None,
    ) -> None:
        self.client_id = client_id
        self.name = name
        self.email = email
        self.plan = plan
        self.stripe_customer_id = stripe_customer_id
        self.created_at = datetime.utcnow()
        self.last_activity: Optional[datetime] = None
        self.is_active = True
        self.monthly_spend: float = 0.0
        self.upsell_opportunities: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "name": self.name,
            "email": self.email,
            "plan": self.plan,
            "stripe_customer_id": self.stripe_customer_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_active": self.is_active,
            "monthly_spend": self.monthly_spend,
            "upsell_opportunities": self.upsell_opportunities,
        }


class ClientManager:
    """Manages the lifecycle of ECO-IA clients."""

    def __init__(self) -> None:
        self._clients: Dict[str, Client] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_client(
        self,
        name: str,
        email: str,
        plan: str = "basic",
        stripe_customer_id: Optional[str] = None,
    ) -> Client:
        client_id = str(uuid.uuid4())
        client = Client(
            client_id=client_id,
            name=name,
            email=email,
            plan=plan,
            stripe_customer_id=stripe_customer_id,
        )
        self._clients[client_id] = client
        logger.info("Client created: %s (%s)", name, client_id)
        return client

    def get_client(self, client_id: str) -> Optional[Client]:
        return self._clients.get(client_id)

    def list_clients(self, active_only: bool = True) -> List[Client]:
        if active_only:
            return [c for c in self._clients.values() if c.is_active]
        return list(self._clients.values())

    def deactivate_client(self, client_id: str) -> bool:
        client = self._clients.get(client_id)
        if client:
            client.is_active = False
            logger.info("Client deactivated: %s", client_id)
            return True
        return False

    def upgrade_plan(self, client_id: str, new_plan: str) -> bool:
        client = self._clients.get(client_id)
        if client:
            old_plan = client.plan
            client.plan = new_plan
            logger.info("Client '%s' upgraded from '%s' to '%s'.", client_id, old_plan, new_plan)
            return True
        return False

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def record_activity(self, client_id: str) -> None:
        client = self._clients.get(client_id)
        if client:
            client.last_activity = datetime.utcnow()

    def detect_upsell_opportunities(self) -> List[Dict[str, Any]]:
        """Identify clients that could benefit from a plan upgrade."""
        opportunities = []
        for client in self._clients.values():
            if not client.is_active:
                continue
            if client.plan == "basic" and client.monthly_spend > 50:
                opportunities.append(
                    {
                        "client_id": client.client_id,
                        "name": client.name,
                        "current_plan": client.plan,
                        "suggested_plan": "pro",
                        "reason": "High monthly spend on basic plan",
                    }
                )
            elif client.plan == "pro" and client.monthly_spend > 200:
                opportunities.append(
                    {
                        "client_id": client.client_id,
                        "name": client.name,
                        "current_plan": client.plan,
                        "suggested_plan": "enterprise",
                        "reason": "High monthly spend on pro plan",
                    }
                )
        return opportunities

    def get_summary(self) -> Dict[str, Any]:
        active = self.list_clients(active_only=True)
        return {
            "total_clients": len(self._clients),
            "active_clients": len(active),
            "plans": {plan: sum(1 for c in active if c.plan == plan) for plan in {"basic", "pro", "enterprise"}},
        }
