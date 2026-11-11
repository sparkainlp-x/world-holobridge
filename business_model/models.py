"""Core recurring-revenue and break-even model.

All outputs are modelled projections. They require measured costs, supplier
quotes, signed contracts, and customer data before being treated as evidence
of commercial performance.
"""

from dataclasses import dataclass, field
from math import ceil
from typing import Dict, List, Optional


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


@dataclass
class RentalRecovery:
    """Hardware rental cost-recovery calculation.

    Rental price recovers the capital outlay over the planned service life,
    then adds monthly maintenance and a required rental margin. Rental
    revenue is tracked separately from creative-service revenue.
    """

    equipment_landed_cost: float
    installation_cost: float
    risk_reserve: float = 0.0
    planned_service_life_months: int = 36
    monthly_maintenance: float = 0.0
    required_rental_margin: float = 0.0

    def __post_init__(self) -> None:
        if self.planned_service_life_months <= 0:
            raise ValueError("planned_service_life_months must be positive")
        if self.equipment_landed_cost < 0:
            raise ValueError("equipment_landed_cost must not be negative")
        if self.installation_cost < 0:
            raise ValueError("installation_cost must not be negative")
        if self.risk_reserve < 0:
            raise ValueError("risk_reserve must not be negative")

    @property
    def capital_to_recover(self) -> float:
        """Return equipment + installation + risk reserve."""
        return (
            self.equipment_landed_cost
            + self.installation_cost
            + self.risk_reserve
        )

    @property
    def monthly_capital_recovery(self) -> float:
        """Return the capital outlay spread over the service life."""
        return self.capital_to_recover / self.planned_service_life_months

    @property
    def rental_price(self) -> float:
        """Return the required monthly rental price.

        rental price = (equipment + installation + risk reserve)
            / planned service life in months
            + monthly maintenance + required rental margin
        """
        return (
            self.monthly_capital_recovery
            + self.monthly_maintenance
            + self.required_rental_margin
        )


@dataclass
class Sensitivity:
    """Sensitivity analysis for renewal, churn, payment delay, and overruns.

    All parameters are modelled assumptions, not measured customer behaviour.
    """

    renewal_rate: float = 0.0
    customer_churn_monthly: float = 0.0
    payment_delay_days: int = 0
    support_overrun_multiplier: float = 1.0
    equipment_replacement_reserve_multiplier: float = 1.0
    downside_scenarios: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.renewal_rate <= 1.0:
            raise ValueError("renewal_rate must be between 0 and 1")
        if not 0.0 <= self.customer_churn_monthly <= 1.0:
            raise ValueError("customer_churn_monthly must be between 0 and 1")
        if self.payment_delay_days < 0:
            raise ValueError("payment_delay_days must not be negative")
        if self.support_overrun_multiplier < 0:
            raise ValueError("support_overrun_multiplier must not be negative")
        if self.equipment_replacement_reserve_multiplier < 0:
            raise ValueError(
                "equipment_replacement_reserve_multiplier must not be negative"
            )

    def retained_monthly_revenue(self, model: BusinessModel) -> float:
        """Return monthly revenue after one month of churn."""
        return model.monthly_recurring_revenue * (1.0 - self.customer_churn_monthly)

    def adjusted_monthly_variable_costs(
        self, model: BusinessModel, support_hours_cost: float = 0.0
    ) -> float:
        """Return variable costs with the support-overrun multiplier applied.

        Only the support-hours cost line is scaled; every other variable
        cost line is unchanged.
        """
        base = model.monthly_variable_costs
        return (
            base
            - support_hours_cost
            + support_hours_cost * self.support_overrun_multiplier
        )

    def adjusted_monthly_contribution(
        self, model: BusinessModel, support_hours_cost: float = 0.0
    ) -> float:
        """Return contribution after churn and support overrun."""
        return self.retained_monthly_revenue(model) - self.adjusted_monthly_variable_costs(
            model, support_hours_cost
        )

    def payment_delay_cash_impact(self, model: BusinessModel) -> float:
        """Return working capital tied up by the payment delay.

        A delay of D days holds back roughly MRR * D / 30 of cash.
        This is a cash-flow timing effect, not a profit-and-loss cost.
        """
        return model.monthly_recurring_revenue * self.payment_delay_days / 30.0

    def adjusted_rental_price(self, rental: RentalRecovery) -> float:
        """Return the rental price with the replacement-reserve multiplier.

        The multiplier scales only the risk-reserve portion of the capital
        to recover, not the equipment or installation cost.
        """
        adjusted_reserve = (
            rental.risk_reserve * self.equipment_replacement_reserve_multiplier
        )
        adjusted_capital = (
            rental.equipment_landed_cost
            + rental.installation_cost
            + adjusted_reserve
        )
        return (
            adjusted_capital / rental.planned_service_life_months
            + rental.monthly_maintenance
            + rental.required_rental_margin
        )

    def run_downside_scenarios(
        self,
        model: BusinessModel,
        support_hours_cost: float = 0.0,
        rental: Optional[RentalRecovery] = None,
    ) -> List[Dict[str, object]]:
        """Run each named downside scenario and report its outcome.

        Each scenario is a dict with a "name" and parameter overrides for
        the sensitivity fields. The base model is never mutated.
        """
        results: List[Dict[str, object]] = []
        for scenario in self.downside_scenarios:
            name = str(scenario.get("name", "unnamed"))
            overrides = {
                key: scenario[key]
                for key in (
                    "renewal_rate",
                    "customer_churn_monthly",
                    "payment_delay_days",
                    "support_overrun_multiplier",
                    "equipment_replacement_reserve_multiplier",
                )
                if key in scenario
            }
            adjusted = Sensitivity(
                renewal_rate=float(
                    overrides.get("renewal_rate", self.renewal_rate)
                ),
                customer_churn_monthly=float(
                    overrides.get(
                        "customer_churn_monthly", self.customer_churn_monthly
                    )
                ),
                payment_delay_days=int(
                    overrides.get("payment_delay_days", self.payment_delay_days)
                ),
                support_overrun_multiplier=float(
                    overrides.get(
                        "support_overrun_multiplier", self.support_overrun_multiplier
                    )
                ),
                equipment_replacement_reserve_multiplier=float(
                    overrides.get(
                        "equipment_replacement_reserve_multiplier",
                        self.equipment_replacement_reserve_multiplier,
                    )
                ),
            )
            adjusted_contribution = adjusted.adjusted_monthly_contribution(
                model, support_hours_cost
            )
            active = model.active_subscriptions
            average = (
                adjusted_contribution / len(active) if active else 0.0
            )
            if average <= 0:
                break_even: int = -1
            else:
                break_even = ceil(model.monthly_fixed_costs / average)
            entry: Dict[str, object] = {
                "name": name,
                "adjusted_monthly_contribution": adjusted_contribution,
                "break_even_subscriptions": break_even,
                "payment_delay_cash_impact": adjusted.payment_delay_cash_impact(
                    model
                ),
            }
            if rental is not None:
                entry["adjusted_rental_price"] = adjusted.adjusted_rental_price(
                    rental
                )
            results.append(entry)
        return results


@dataclass
class ContentCapacity:
    """Content-capacity workload model.

    Workload is measured in asset-equivalent units: each monthly asset
    counts as one unit, and revisions, translations, accessibility checks,
    and support hours each add a configurable weight per unit of work.

    workload = assets
        + revisions * revision_multiplier
        + translations * translation_multiplier
        + accessibility checks * accessibility_check_multiplier
        + support hours * support_hour_multiplier

    The multipliers are transparent planning assumptions, not measured
    effort. Capacity utilization above 1.0 means the planned workload
    exceeds the team's monthly capacity.
    """

    monthly_assets: int = 0
    revisions: int = 0
    translations: int = 0
    accessibility_checks: int = 0
    support_hours: float = 0.0
    revision_multiplier: float = 0.5
    translation_multiplier: float = 1.0
    accessibility_check_multiplier: float = 0.5
    support_hour_multiplier: float = 0.25
    monthly_capacity_units: float = 0.0

    def __post_init__(self) -> None:
        if self.monthly_assets < 0:
            raise ValueError("monthly_assets must not be negative")
        if self.revisions < 0:
            raise ValueError("revisions must not be negative")
        if self.translations < 0:
            raise ValueError("translations must not be negative")
        if self.accessibility_checks < 0:
            raise ValueError("accessibility_checks must not be negative")
        if self.support_hours < 0:
            raise ValueError("support_hours must not be negative")
        if self.monthly_capacity_units < 0:
            raise ValueError("monthly_capacity_units must not be negative")

    @property
    def workload_units(self) -> float:
        """Return the planned monthly workload in asset-equivalent units."""
        return (
            self.monthly_assets
            + self.revisions * self.revision_multiplier
            + self.translations * self.translation_multiplier
            + self.accessibility_checks * self.accessibility_check_multiplier
            + self.support_hours * self.support_hour_multiplier
        )

    @property
    def capacity_utilization(self) -> Optional[float]:
        """Return workload as a fraction of monthly capacity.

        Returns None when no capacity is recorded, because utilization
        cannot be computed without a capacity figure.
        """
        if self.monthly_capacity_units <= 0:
            return None
        return self.workload_units / self.monthly_capacity_units

    @property
    def over_capacity(self) -> bool:
        """Return True when planned workload exceeds monthly capacity."""
        utilization = self.capacity_utilization
        return utilization is not None and utilization > 1.0

    @property
    def overage_units(self) -> float:
        """Return workload units above capacity, or 0 when within capacity."""
        if self.monthly_capacity_units <= 0:
            return 0.0
        return max(0.0, self.workload_units - self.monthly_capacity_units)


@dataclass
class WorkforceRole:
    """A single paid role in the disability-led workforce."""

    name: str
    hours_monthly: float
    hourly_rate: float
    accommodation_monthly: float = 0.0

    def __post_init__(self) -> None:
        if self.hours_monthly < 0:
            raise ValueError("hours_monthly must not be negative")
        if self.hourly_rate < 0:
            raise ValueError("hourly_rate must not be negative")
        if self.accommodation_monthly < 0:
            raise ValueError("accommodation_monthly must not be negative")

    @property
    def monthly_labour_cost(self) -> float:
        """Return hours times hourly rate for this role."""
        return self.hours_monthly * self.hourly_rate

    @property
    def monthly_cost(self) -> float:
        """Return labour cost plus accommodation cost for this role."""
        return self.monthly_labour_cost + self.accommodation_monthly


@dataclass
class Workforce:
    """Workforce cost tracking with subsidy separation.

    Subsidy support is restricted funding and is always reported
    separately from customer subscription revenue. The post-subsidy
    cost is what the business must carry once the subsidy ends.
    """

    roles: List[WorkforceRole] = field(default_factory=list)
    subsidy_support_monthly: float = 0.0
    subsidy_end_date: Optional[str] = None
    funding_independent_continuation_plan: bool = False

    def __post_init__(self) -> None:
        if self.subsidy_support_monthly < 0:
            raise ValueError("subsidy_support_monthly must not be negative")

    @property
    def paid_hours_monthly(self) -> float:
        """Return total paid hours across all roles."""
        return sum(role.hours_monthly for role in self.roles)

    @property
    def monthly_labour_cost(self) -> float:
        """Return total labour cost across all roles."""
        return sum(role.monthly_labour_cost for role in self.roles)

    @property
    def monthly_accommodation_costs(self) -> float:
        """Return total accommodation costs across all roles."""
        return sum(role.accommodation_monthly for role in self.roles)

    @property
    def monthly_workforce_cost(self) -> float:
        """Return labour plus accommodation costs."""
        return self.monthly_labour_cost + self.monthly_accommodation_costs

    @property
    def monthly_net_cost(self) -> float:
        """Return workforce cost after subsidy support."""
        return self.monthly_workforce_cost - self.subsidy_support_monthly

    @property
    def post_subsidy_monthly_cost(self) -> float:
        """Return the monthly cost once subsidy support ends."""
        return self.monthly_workforce_cost

    @property
    def subsidy_covers_payroll(self) -> bool:
        """Return True when subsidy covers the full workforce cost."""
        return (
            self.monthly_workforce_cost > 0
            and self.subsidy_support_monthly >= self.monthly_workforce_cost
        )

    @property
    def continuation_risk(self) -> bool:
        """Return True when payroll depends on subsidy with no backup plan.

        True only when the subsidy covers the full workforce cost and no
        funding-independent continuation plan is recorded.
        """
        return (
            self.subsidy_covers_payroll
            and not self.funding_independent_continuation_plan
        )


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
