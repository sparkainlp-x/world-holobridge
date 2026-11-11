"""Tests for the recurring-revenue and break-even model."""

from business_model.models import BusinessModel, Subscription


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
