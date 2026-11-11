#!/usr/bin/env python3
"""Generate a modelled recurring-revenue and break-even report.

Usage:

    python scripts/business_model_report.py business_model/business_model_template.json

The output is a modelled projection. It is not evidence of realized revenue,
profitability, market demand, or scientific validation.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from business_model.models import BusinessModel, Subscription


def load_model(path: Path) -> BusinessModel:
    """Load a business-model JSON file and return an aggregate model."""
    data = json.loads(path.read_text(encoding="utf-8"))
    model = data["business_model"]

    revenue = model["recurring_revenue"]
    costs = model["monthly_variable_costs"]
    recurring_revenue = sum(float(value) for value in revenue.values())
    variable_cost = sum(float(value) for value in costs.values())

    return BusinessModel(
        monthly_fixed_costs=float(model["monthly_fixed_costs"]),
        subscriptions=[
            Subscription(
                name="managed_holo_service",
                monthly_revenue=recurring_revenue,
                monthly_variable_cost=variable_cost,
                contract_months=int(model["pricing_model"]["contract_months"]),
            )
        ],
    )


def build_report(model: BusinessModel) -> Dict[str, Any]:
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
        "limitations": [
            "Does not include taxes unless explicitly added.",
            "Does not include customer acquisition cost.",
            "Does not model churn, payment delay, or renewal risk.",
            "Does not validate supplier pricing or market demand.",
            "Does not establish workforce sustainability or employment outcomes.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a modelled recurring-revenue and break-even report."
    )
    parser.add_argument("plan", type=Path, help="Path to a business-model JSON file")
    args = parser.parse_args()

    model = load_model(args.plan)
    print(json.dumps(build_report(model), indent=2))


if __name__ == "__main__":
    main()
