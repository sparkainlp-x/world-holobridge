"""Business-model extension for World-HoloBridge.

This module models proposed recurring revenue, delivery costs, contribution,
and break-even subscription counts. It does not establish measured revenue,
market demand, profitability, or scientific validation.
"""

from .models import BusinessModel, Subscription

__all__ = ["BusinessModel", "Subscription"]
