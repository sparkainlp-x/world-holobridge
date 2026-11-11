"""Tests for the recurring-revenue and break-even model."""

import pytest

from business_model.models import (
    BusinessModel,
    ContentCapacity,
    RentalRecovery,
    Sensitivity,
    Subscription,
    Workforce,
    WorkforceRole,
)


def test_break_even_rounds_up():
    model = BusinessModel(
        monthly_fixed_costs=1000.00,
        subscriptions=[
            Subscription(
                name="service",
                monthly_revenue=1300.00,
                monthly_variable_cost=300.00,
            )
        ],
    )

    assert model.monthly_recurring_revenue == 1300.00
    assert model.monthly_variable_costs == 300.00
    assert model.monthly_contribution == 1000.00
    assert model.average_monthly_contribution == 1000.00
    assert model.break_even_subscriptions == 1
    assert model.annualized_run_rate() == 15600.00


def test_break_even_requires_multiple_customers_when_contribution_is_small():
    model = BusinessModel(
        monthly_fixed_costs=1000.00,
        subscriptions=[
            Subscription(
                name="service",
                monthly_revenue=1300.00,
                monthly_variable_cost=1200.00,
            )
        ],
    )

    assert model.monthly_contribution == 100.00
    assert model.break_even_subscriptions == 10


def test_negative_contribution_returns_no_break_even():
    model = BusinessModel(
        monthly_fixed_costs=1000.00,
        subscriptions=[
            Subscription(
                name="service",
                monthly_revenue=1000.00,
                monthly_variable_cost=1200.00,
            )
        ],
    )

    assert model.monthly_contribution == -200.00
    assert model.break_even_subscriptions == -1


def test_zero_customers_returns_no_break_even():
    model = BusinessModel(monthly_fixed_costs=1000.00)

    assert model.monthly_recurring_revenue == 0.00
    assert model.monthly_variable_costs == 0.00
    assert model.monthly_contribution == 0.00
    assert model.average_monthly_contribution == 0.00
    assert model.break_even_subscriptions == -1


def test_inactive_subscription_is_excluded():
    model = BusinessModel(
        monthly_fixed_costs=1000.00,
        subscriptions=[
            Subscription(
                name="active",
                monthly_revenue=1300.00,
                monthly_variable_cost=300.00,
                active=True,
            ),
            Subscription(
                name="inactive",
                monthly_revenue=1300.00,
                monthly_variable_cost=300.00,
                active=False,
            ),
        ],
    )

    assert len(model.active_subscriptions) == 1
    assert model.monthly_recurring_revenue == 1300.00
    assert model.break_even_subscriptions == 1


def test_zero_contribution_returns_no_break_even():
    model = BusinessModel(
        monthly_fixed_costs=1000.00,
        subscriptions=[
            Subscription(
                name="service",
                monthly_revenue=1300.00,
                monthly_variable_cost=1300.00,
            )
        ],
    )

    assert model.monthly_contribution == 0.00
    assert model.average_monthly_contribution == 0.00
    assert model.break_even_subscriptions == -1


# --- Sensitivity analysis ---


def _base_model():
    return BusinessModel(
        monthly_fixed_costs=2000.00,
        subscriptions=[
            Subscription(
                name="service",
                monthly_revenue=1300.00,
                monthly_variable_cost=300.00,
            )
        ],
    )


def test_churn_reduces_retained_revenue():
    sensitivity = Sensitivity(customer_churn_monthly=0.10)
    model = _base_model()

    assert sensitivity.retained_monthly_revenue(model) == 1170.00
    assert sensitivity.adjusted_monthly_contribution(model) == 870.00


def test_support_overrun_scales_only_support_cost():
    sensitivity = Sensitivity(support_overrun_multiplier=1.5)
    model = _base_model()

    # Support-hours line is 200 of the 300 variable cost.
    assert (
        sensitivity.adjusted_monthly_variable_costs(model, 200.00) == 400.00
    )
    assert sensitivity.adjusted_monthly_contribution(model, 200.00) == 900.00


def test_payment_delay_ties_up_working_capital():
    sensitivity = Sensitivity(payment_delay_days=30)
    model = _base_model()

    assert sensitivity.payment_delay_cash_impact(model) == 1300.00


def test_invalid_sensitivity_parameters_raise():
    with pytest.raises(ValueError):
        Sensitivity(renewal_rate=1.5)
    with pytest.raises(ValueError):
        Sensitivity(customer_churn_monthly=-0.1)
    with pytest.raises(ValueError):
        Sensitivity(payment_delay_days=-5)
    with pytest.raises(ValueError):
        Sensitivity(support_overrun_multiplier=-1.0)
    with pytest.raises(ValueError):
        Sensitivity(equipment_replacement_reserve_multiplier=-1.0)


def test_downside_scenario_changes_break_even():
    sensitivity = Sensitivity(
        downside_scenarios=[
            {"name": "high_churn", "customer_churn_monthly": 0.5},
        ]
    )
    model = _base_model()

    results = sensitivity.run_downside_scenarios(model)
    assert len(results) == 1
    assert results[0]["name"] == "high_churn"
    # Retained 650, contribution 350, break-even ceil(2000 / 350) = 6.
    assert results[0]["adjusted_monthly_contribution"] == 350.00
    assert results[0]["break_even_subscriptions"] == 6


def test_downside_scenario_with_no_positive_contribution_returns_no_break_even():
    sensitivity = Sensitivity(
        downside_scenarios=[
            {"name": "total_churn", "customer_churn_monthly": 1.0},
        ]
    )
    model = _base_model()

    results = sensitivity.run_downside_scenarios(model)
    assert results[0]["adjusted_monthly_contribution"] == -300.00
    assert results[0]["break_even_subscriptions"] == -1


# --- Rental recovery ---


def test_rental_price_formula():
    rental = RentalRecovery(
        equipment_landed_cost=1200.00,
        installation_cost=300.00,
        risk_reserve=300.00,
        planned_service_life_months=36,
        monthly_maintenance=50.00,
        required_rental_margin=100.00,
    )

    assert rental.capital_to_recover == 1800.00
    assert rental.monthly_capital_recovery == 50.00
    assert rental.rental_price == 200.00


def test_rental_price_with_zero_capital_is_maintenance_plus_margin():
    rental = RentalRecovery(
        equipment_landed_cost=0.00,
        installation_cost=0.00,
        risk_reserve=0.00,
        planned_service_life_months=36,
        monthly_maintenance=50.00,
        required_rental_margin=100.00,
    )

    assert rental.rental_price == 150.00


def test_rental_requires_positive_service_life():
    with pytest.raises(ValueError):
        RentalRecovery(
            equipment_landed_cost=1200.00,
            installation_cost=300.00,
            planned_service_life_months=0,
        )


def test_replacement_reserve_multiplier_scales_only_reserve():
    rental = RentalRecovery(
        equipment_landed_cost=1200.00,
        installation_cost=300.00,
        risk_reserve=300.00,
        planned_service_life_months=36,
        monthly_maintenance=50.00,
        required_rental_margin=100.00,
    )
    sensitivity = Sensitivity(equipment_replacement_reserve_multiplier=2.0)

    # Reserve 600: capital 2100, monthly 58.33, price 208.33.
    assert sensitivity.adjusted_rental_price(rental) == pytest.approx(208.33, abs=0.01)


# --- Content capacity ---


def test_workload_formula():
    capacity = ContentCapacity(
        monthly_assets=10,
        revisions=4,
        translations=2,
        accessibility_checks=4,
        support_hours=8.0,
        monthly_capacity_units=20.0,
    )

    # 10 + 4*0.5 + 2*1.0 + 4*0.5 + 8*0.25 = 18.0
    assert capacity.workload_units == 18.0
    assert capacity.capacity_utilization == 0.9
    assert capacity.over_capacity is False
    assert capacity.overage_units == 0.0


def test_over_capacity_reports_utilization_and_overage():
    capacity = ContentCapacity(
        monthly_assets=20,
        revisions=10,
        translations=5,
        accessibility_checks=10,
        support_hours=20.0,
        monthly_capacity_units=20.0,
    )

    # 20 + 5 + 5 + 5 + 5 = 40 units against 20 capacity.
    assert capacity.workload_units == 40.0
    assert capacity.capacity_utilization == 2.0
    assert capacity.over_capacity is True
    assert capacity.overage_units == 20.0


def test_zero_capacity_returns_no_utilization():
    capacity = ContentCapacity(monthly_assets=5, monthly_capacity_units=0.0)

    assert capacity.capacity_utilization is None
    assert capacity.over_capacity is False
    assert capacity.overage_units == 0.0


def test_negative_workload_inputs_raise():
    with pytest.raises(ValueError):
        ContentCapacity(monthly_assets=-1)
    with pytest.raises(ValueError):
        ContentCapacity(support_hours=-1.0)


# --- Workforce cost tracking ---


def _workforce_with_role():
    return Workforce(
        roles=[
            WorkforceRole(
                name="creative_lead",
                hours_monthly=40.0,
                hourly_rate=25.00,
                accommodation_monthly=100.00,
            )
        ],
        subsidy_support_monthly=500.00,
        subsidy_end_date="2027-06-30",
        funding_independent_continuation_plan=False,
    )


def test_workforce_cost_and_net_after_subsidy():
    workforce = _workforce_with_role()

    assert workforce.paid_hours_monthly == 40.0
    assert workforce.monthly_labour_cost == 1000.00
    assert workforce.monthly_accommodation_costs == 100.00
    assert workforce.monthly_workforce_cost == 1100.00
    assert workforce.monthly_net_cost == 600.00
    assert workforce.post_subsidy_monthly_cost == 1100.00


def test_workforce_with_no_roles_costs_nothing():
    workforce = Workforce()

    assert workforce.paid_hours_monthly == 0.0
    assert workforce.monthly_workforce_cost == 0.0
    assert workforce.monthly_net_cost == 0.0
    assert workforce.subsidy_covers_payroll is False
    assert workforce.continuation_risk is False


def test_continuation_risk_when_subsidy_covers_payroll_without_plan():
    workforce = Workforce(
        roles=[
            WorkforceRole(
                name="support",
                hours_monthly=20.0,
                hourly_rate=20.00,
            )
        ],
        subsidy_support_monthly=500.00,
        funding_independent_continuation_plan=False,
    )

    assert workforce.monthly_workforce_cost == 400.00
    assert workforce.subsidy_covers_payroll is True
    assert workforce.continuation_risk is True


def test_continuation_plan_clears_risk():
    workforce = _workforce_with_role()
    workforce.subsidy_support_monthly = 2000.00
    workforce.funding_independent_continuation_plan = True

    assert workforce.subsidy_covers_payroll is True
    assert workforce.continuation_risk is False


def test_negative_workforce_inputs_raise():
    with pytest.raises(ValueError):
        WorkforceRole(name="role", hours_monthly=-1.0, hourly_rate=25.00)
    with pytest.raises(ValueError):
        Workforce(subsidy_support_monthly=-100.00)
