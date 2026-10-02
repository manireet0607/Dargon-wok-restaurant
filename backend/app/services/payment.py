"""Payment is kept behind a small interface so an online gateway (Razorpay, Stripe, ...)
can be added later without touching the order code. Only Cash on Delivery exists now."""
from abc import ABC, abstractmethod
from decimal import Decimal


class PaymentProvider(ABC):
    method: str

    @abstractmethod
    def initial_status(self) -> str:
        """Payment status when the order is created."""

    @abstractmethod
    def on_delivered(self) -> str | None:
        """New payment status when the order is delivered (None = no change)."""


class CashOnDelivery(PaymentProvider):
    method = "cod"

    def initial_status(self) -> str:
        return "pending"

    def on_delivered(self) -> str | None:
        return "paid"  # cash is collected at the door


_PROVIDERS: dict[str, PaymentProvider] = {"cod": CashOnDelivery()}


def get_payment_provider(method: str) -> PaymentProvider:
    try:
        return _PROVIDERS[method]
    except KeyError:
        raise ValueError(f"Unsupported payment method: {method}")


def register_provider(provider: PaymentProvider) -> None:
    _PROVIDERS[provider.method] = provider


__all__ = ["PaymentProvider", "CashOnDelivery", "get_payment_provider", "register_provider", "Decimal"]
