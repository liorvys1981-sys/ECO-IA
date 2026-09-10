"""Stripe service facade for the requested layout."""

from agents.monetization.billing import BillingManager


class StripeService(BillingManager):
    """Compatibility alias around the existing billing manager."""


__all__ = ["StripeService"]
