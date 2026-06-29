"""Billing management via Stripe API."""

import logging
import os
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class BillingManager:
    """Handles automatic invoicing and payment collection through Stripe."""

    def __init__(self, stripe_api_key: Optional[str] = None) -> None:
        self._api_key = stripe_api_key or os.getenv("STRIPE_SECRET_KEY", "")
        self._stripe_available = False
        self._invoices: List[Dict[str, Any]] = []
        self._init_stripe()

    def _init_stripe(self) -> None:
        try:
            import stripe  # type: ignore[import]

            stripe.api_key = self._api_key
            self._stripe = stripe
            self._stripe_available = True
            logger.info("Stripe initialised.")
        except ImportError:
            logger.warning("stripe package not installed; billing in simulation mode.")

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    async def create_customer(self, email: str, name: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new Stripe customer."""
        if not self._stripe_available:
            return self._simulate("create_customer", email=email, name=name)
        customer = self._stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {},
        )
        logger.info("Customer created: %s", customer["id"])
        return dict(customer)

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve a Stripe customer by ID."""
        if not self._stripe_available:
            return self._simulate("get_customer", customer_id=customer_id)
        return dict(self._stripe.Customer.retrieve(customer_id))

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
    ) -> Dict[str, Any]:
        """Subscribe a customer to a plan."""
        if not self._stripe_available:
            return self._simulate("create_subscription", customer_id=customer_id, price_id=price_id)
        params: Dict[str, Any] = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }
        if trial_days > 0:
            params["trial_period_days"] = trial_days
        subscription = self._stripe.Subscription.create(**params)
        logger.info("Subscription created: %s", subscription["id"])
        return dict(subscription)

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel an active subscription."""
        if not self._stripe_available:
            return self._simulate("cancel_subscription", subscription_id=subscription_id)
        subscription = self._stripe.Subscription.delete(subscription_id)
        logger.info("Subscription cancelled: %s", subscription_id)
        return dict(subscription)

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    async def create_invoice(self, customer_id: str, amount_cents: int, description: str) -> Dict[str, Any]:
        """Create and finalise an invoice."""
        if not self._stripe_available:
            invoice_sim = self._simulate(
                "create_invoice",
                customer_id=customer_id,
                amount=amount_cents,
                description=description,
            )
            self._invoices.append(invoice_sim)
            return invoice_sim

        invoice_item = self._stripe.InvoiceItem.create(
            customer=customer_id,
            amount=amount_cents,
            currency="usd",
            description=description,
        )
        invoice = self._stripe.Invoice.create(customer=customer_id)
        self._stripe.Invoice.finalize_invoice(invoice["id"])
        result = dict(invoice)
        self._invoices.append(result)
        logger.info("Invoice created: %s", invoice["id"])
        return result

    async def list_invoices(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List invoices, optionally filtered by customer."""
        if not self._stripe_available:
            return self._invoices
        params: Dict[str, Any] = {"limit": 100}
        if customer_id:
            params["customer"] = customer_id
        invoices = self._stripe.Invoice.list(**params)
        return [dict(inv) for inv in invoices["data"]]

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------

    def _simulate(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        import uuid

        logger.debug("Simulating Stripe action '%s' with %s", action, kwargs)
        return {"id": f"sim_{uuid.uuid4().hex[:8]}", "action": action, "params": kwargs, "status": "simulated"}

    def get_revenue_summary(self) -> Dict[str, Any]:
        """Return a summary of collected revenue (simulation)."""
        return {
            "total_invoices": len(self._invoices),
            "stripe_available": self._stripe_available,
        }
