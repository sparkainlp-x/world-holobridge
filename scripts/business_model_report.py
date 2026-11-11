#!/usr/bin/env python3
"""Generate a modelled recurring-revenue and break-even report.

Usage:

    python scripts/business_model_report.py business_model/business_model_template.json

The output is a modelled projection. It is not evidence of realized revenue,
profitability, market demand, or scientific validation.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Allow running as `python scripts/business_model_report.py ...` from the
# repository root without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from business_model.models import (  # noqa: E402
    BusinessModel,
    ContentCapacity,
    RentalRecovery,
    Sensitivity,
    Subscription,
    Workforce,
    WorkforceRole,
)


def _sum_cost_lines(value: Any) -> float:
    """Return the total of a cost section given as a dict or a scalar."""
    if isinstance(value, dict):
        return sum(float(item) for item in value.values())
    return float(value)


def _rental_field(section: Dict[str, Any], new: str, old: str, default: float) -> float:
    """Read a rental field, accepting the current name or the legacy name."""
    if new in section:
        return float(section[new])
    if old in section:
        return float(section[old])
    return default


def load_model(path: Path) -> Tuple[
    BusinessModel, Sensitivity, RentalRecovery, ContentCapacity, Workforce, float
]:
    """Load a business-model JSON file and return the model objects.

    Returns the aggregate business model, sensitivity, rental recovery,
    content capacity, workforce, and the support-hours variable-cost line
    (needed to apply the support-overrun multiplier).
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    model = data["business_model"]

    revenue = model["recurring_revenue"]
    costs = model["monthly_variable_costs"]
    recurring_revenue = sum(float(value) for value in revenue.values())
    variable_cost = sum(float(value) for value in costs.values())
    support_hours_cost = float(costs.get("support_hours", 0.0))

    business = BusinessModel(
        monthly_fixed_costs=_sum_cost_lines(model["monthly_fixed_costs"]),
        subscriptions=[
            Subscription(
                name="managed_holo_service",
                monthly_revenue=recurring_revenue,
                monthly_variable_cost=variable_cost,
                contract_months=int(model["pricing_model"]["contract_months"]),
            )
        ],
    )

    sensitivity_data = model.get("sensitivity", {})
    sensitivity = Sensitivity(
        renewal_rate=float(sensitivity_data.get("renewal_rate", 0.0)),
        customer_churn_monthly=float(
            sensitivity_data.get("customer_churn_monthly", 0.0)
        ),
        payment_delay_days=int(sensitivity_data.get("payment_delay_days", 0)),
        support_overrun_multiplier=float(
            sensitivity_data.get("support_overrun_multiplier", 1.0)
        ),
        equipment_replacement_reserve_multiplier=float(
            sensitivity_data.get(
                "equipment_replacement_reserve_multiplier", 1.0
            )
        ),
        downside_scenarios=list(
            sensitivity_data.get("downside_scenarios", [])
        ),
    )

    rental_data = model.get("rental_recovery", {})
    rental = RentalRecovery(
        equipment_landed_cost=float(rental_data.get("equipment_landed_cost", 0.0)),
        installation_cost=float(rental_data.get("installation_cost", 0.0)),
        risk_reserve=_rental_field(
            rental_data, "risk_reserve", "risk_reserve_monthly", 0.0
        ),
        planned_service_life_months=int(
            rental_data.get("planned_service_life_months", 36)
        ),
        monthly_maintenance=_rental_field(
            rental_data, "monthly_maintenance", "maintenance_monthly", 0.0
        ),
        required_rental_margin=_rental_field(
            rental_data,
            "required_rental_margin",
            "required_rental_margin_monthly",
            0.0,
        ),
    )

    capacity_data = model.get("content_capacity", {})
    capacity = ContentCapacity(
        monthly_assets=int(capacity_data.get("monthly_assets", 0)),
        revisions=int(capacity_data.get("revisions", 0)),
        translations=int(capacity_data.get("translations", 0)),
        accessibility_checks=int(capacity_data.get("accessibility_checks", 0)),
        support_hours=float(capacity_data.get("support_hours", 0.0)),
        revision_multiplier=float(capacity_data.get("revision_multiplier", 0.5)),
        translation_multiplier=float(
            capacity_data.get("translation_multiplier", 1.0)
        ),
        accessibility_check_multiplier=float(
            capacity_data.get("accessibility_check_multiplier", 0.5)
        ),
        support_hour_multiplier=float(
            capacity_data.get("support_hour_multiplier", 0.25)
        ),
        monthly_capacity_units=float(
            capacity_data.get("monthly_capacity_units", 0.0)
        ),
    )

    workforce_data = model.get("workforce", {})
    roles: list = []
    for entry in workforce_data.get("paid_roles", []):
        if isinstance(entry, dict):
            roles.append(
                WorkforceRole(
                    name=str(entry.get("name", "role")),
                    hours_monthly=float(entry.get("hours_monthly", 0.0)),
                    hourly_rate=float(entry.get("hourly_rate", 0.0)),
                    accommodation_monthly=float(
                        entry.get("accommodation_monthly", 0.0)
                    ),
                )
            )
        elif isinstance(entry, str):
            roles.append(
                WorkforceRole(name=entry, hours_monthly=0.0, hourly_rate=0.0)
            )
    if not roles:
        # Fall back to the scalar workforce fields as a single generic role.
        hours = float(workforce_data.get("paid_hours_monthly", 0.0))
        rate = float(workforce_data.get("hourly_rate", 0.0))
        accommodation = float(
            workforce_data.get("accommodation_costs_monthly", 0.0)
        )
        if hours > 0 or rate > 0 or accommodation > 0:
            roles.append(
                WorkforceRole(
                    name="paid_work",
                    hours_monthly=hours,
                    hourly_rate=rate,
                    accommodation_monthly=accommodation,
                )
            )
    workforce = Workforce(
        roles=roles,
        subsidy_support_monthly=float(
            workforce_data.get("subsidy_support_monthly", 0.0)
        ),
        subsidy_end_date=workforce_data.get("subsidy_end_date"),
        funding_independent_continuation_plan=bool(
            workforce_data.get(
                "subsidy_independent_plan",
                workforce_data.get(
                    "funding_independent_continuation_plan", False
                ),
            )
        ),
    )

    return business, sensitivity, rental, capacity, workforce, support_hours_cost


def build_report(
    model: BusinessModel,
    sensitivity: Sensitivity,
    rental: RentalRecovery,
    capacity: ContentCapacity,
    workforce: Workforce,
    support_hours_cost: float,
) -> Dict[str, Any]:
    """Return a transparent, modelled commercial report."""
    break_even = model.break_even_subscriptions

    if break_even < 0:
        interpretation = (
            "No break-even count is valid: average monthly contribution "
            "is not positive. Redesign price, scope, or delivery cost."
        )
    else:
        interpretation = (
            "Modelled break-even requires "
            f"{break_even} active subscription(s), assuming unchanged "
            "fixed costs and comparable customer economics."
        )

    adjusted_contribution = sensitivity.adjusted_monthly_contribution(
        model, support_hours_cost
    )
    active = model.active_subscriptions
    adjusted_average = adjusted_contribution / len(active) if active else 0.0
    if adjusted_average <= 0:
        adjusted_break_even: int = -1
    else:
        from math import ceil

        adjusted_break_even = ceil(
            model.monthly_fixed_costs / adjusted_average
        )

    utilization = capacity.capacity_utilization

    return {
        "status": "modelled_not_measured",
        "monthly_recurring_revenue": model.monthly_recurring_revenue,
        "monthly_variable_costs": model.monthly_variable_costs,
        "monthly_contribution": model.monthly_contribution,
        "average_monthly_contribution": model.average_monthly_contribution,
        "monthly_fixed_costs": model.monthly_fixed_costs,
        "break_even_subscriptions": break_even,
        "annualized_run_rate": model.annualized_run_rate(),
        "interpretation": interpretation,
        "sensitivity": {
            "renewal_rate": sensitivity.renewal_rate,
            "customer_churn_monthly": sensitivity.customer_churn_monthly,
            "payment_delay_days": sensitivity.payment_delay_days,
            "support_overrun_multiplier": sensitivity.support_overrun_multiplier,
            "equipment_replacement_reserve_multiplier": (
                sensitivity.equipment_replacement_reserve_multiplier
            ),
            "retained_monthly_revenue": sensitivity.retained_monthly_revenue(
                model
            ),
            "adjusted_monthly_variable_costs": (
                sensitivity.adjusted_monthly_variable_costs(
                    model, support_hours_cost
                )
            ),
            "adjusted_monthly_contribution": adjusted_contribution,
            "adjusted_break_even_subscriptions": adjusted_break_even,
            "payment_delay_cash_impact": (
                sensitivity.payment_delay_cash_impact(model)
            ),
            "downside_scenarios": sensitivity.run_downside_scenarios(
                model, support_hours_cost, rental
            ),
        },
        "rental_recovery": {
            "equipment_landed_cost": rental.equipment_landed_cost,
            "installation_cost": rental.installation_cost,
            "risk_reserve": rental.risk_reserve,
            "capital_to_recover": rental.capital_to_recover,
            "planned_service_life_months": rental.planned_service_life_months,
            "monthly_capital_recovery": rental.monthly_capital_recovery,
            "monthly_maintenance": rental.monthly_maintenance,
            "required_rental_margin": rental.required_rental_margin,
            "rental_price": rental.rental_price,
            "adjusted_rental_price": sensitivity.adjusted_rental_price(rental),
        },
        "content_capacity": {
            "monthly_assets": capacity.monthly_assets,
            "revisions": capacity.revisions,
            "translations": capacity.translations,
            "accessibility_checks": capacity.accessibility_checks,
            "support_hours": capacity.support_hours,
            "workload_units": capacity.workload_units,
            "monthly_capacity_units": capacity.monthly_capacity_units,
            "capacity_utilization": utilization,
            "over_capacity": capacity.over_capacity,
            "overage_units": capacity.overage_units,
        },
        "workforce": {
            "roles": [
                {
                    "name": role.name,
                    "hours_monthly": role.hours_monthly,
                    "hourly_rate": role.hourly_rate,
                    "accommodation_monthly": role.accommodation_monthly,
                    "monthly_cost": role.monthly_cost,
                }
                for role in workforce.roles
            ],
            "paid_hours_monthly": workforce.paid_hours_monthly,
            "monthly_labour_cost": workforce.monthly_labour_cost,
            "monthly_accommodation_costs": workforce.monthly_accommodation_costs,
            "monthly_workforce_cost": workforce.monthly_workforce_cost,
            "subsidy_support_monthly": workforce.subsidy_support_monthly,
            "monthly_net_cost": workforce.monthly_net_cost,
            "post_subsidy_monthly_cost": workforce.post_subsidy_monthly_cost,
            "subsidy_end_date": workforce.subsidy_end_date,
            "funding_independent_continuation_plan": (
                workforce.funding_independent_continuation_plan
            ),
            "subsidy_covers_payroll": workforce.subsidy_covers_payroll,
            "continuation_risk": workforce.continuation_risk,
        },
        "limitations": [
            "Does not include taxes unless explicitly added.",
            "Does not include customer acquisition cost.",
            "Renewal, churn, payment delay, and overrun figures are modelled assumptions, not measured customer behaviour.",
            "Does not validate supplier pricing or market demand.",
            "Does not establish workforce sustainability or employment outcomes.",
            "Rental recovery and creative-service revenue are tracked separately; do not combine them into a single margin.",
            "Subsidy support is restricted funding, separate from customer subscription revenue.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a modelled recurring-revenue and break-even report."
    )
    parser.add_argument("plan", type=Path, help="Path to a business-model JSON file")
    args = parser.parse_args()

    business, sensitivity, rental, capacity, workforce, support_hours_cost = (
        load_model(args.plan)
    )
    report = build_report(
        business, sensitivity, rental, capacity, workforce, support_hours_cost
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
