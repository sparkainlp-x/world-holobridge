"""Core recurring-revenue and break-even model.

All outputs are modelled projections. They require measured costs, supplier
quotes, signed contracts, and customer data before being treated as evidence
of commercial performance.
"""

from dataclasses import dataclass, field
from math import ceil
from typing import List


@dataclass
class Subscription:
    """A recurring customer offering."""

    name: str
    monthly_revenue: float
    monthly_variable_cost: float
    contract_months: int = 12
    active: bool = True

    @property
    def monthly_contribution(self) -> float:
        """Return revenue minus direct monthly delivery cost."""
        return self.monthly_revenue - self.monthly_variable_cost


@dataclass
class BusinessModel:
    """Aggregate recurring-revenue and break-even model."""

    monthly_fixed_costs: float
    subscriptions: List[Subscription] = field(default_factory=list)

    @property
    def active_subscriptions(self) -> List[Subscription]:
        return [subscription for subscription in self.subscriptions if subscription.active]

    @property
    def monthly_recurring_revenue(self) -> float:
        return sum(
            subscription.monthly_revenue
            for subscription in self.active_subscriptions
        )

    @property
    def monthly_variable_costs(self) -> float:
        return sum(
            subscription.monthly_variable_cost
            for subscription in self.active_subscriptions
        )

    @property
    def monthly_contribution(self) -> float:
        return self.monthly_recurring_revenue - self.monthly_variable_costs

    @property
    def average_monthly_contribution(self) -> float:
        active = self.active_subscriptions
        if not active:
            return 0.0
        return self.monthly_contribution / len(active)

    @property
    def break_even_subscriptions(self) -> int:
        """Return the break-even subscription count.

        Returns -1 when average contribution is not positive. A negative or
        zero contribution cannot produce a meaningful break-even count.
        """
        average_contribution = self.average_monthly_contribution
        if average_contribution <= 0:
            return -1
        return ceil(self.monthly_fixed_costs / average_contribution)

    def annualized_run_rate(self) -> float:
        """Return current monthly recurring revenue multiplied by 12."""
        return self.monthly_recurring_revenue * 12
