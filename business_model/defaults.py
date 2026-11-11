"""Default proposal inputs for the Holo Marketing-as-a-Service model.

These values are proposed commercial planning inputs, not measured results,
verified market prices, or commitments from customers or suppliers.
"""

DEFAULT_BUSINESS_MODEL = {
    "currency": "CAD",
    "service_monthly": 1300.00,
    "modification_fee": 500.00,
    "contract_months": 12,
    "monthly_fixed_costs": 0.00,
    "monthly_variable_costs": {
        "ai_inference": 0.00,
        "hosting": 0.00,
        "support_hours": 0.00,
        "content_production": 0.00,
        "accessibility_testing": 0.00,
        "maintenance": 0.00,
        "rental_cost_recovery": 0.00,
        "payment_processing": 0.00,
        "other": 0.00,
    },
    "rental_recovery": {
        "equipment_landed_cost": 0.00,
        "installation_cost": 0.00,
        "risk_reserve": 0.00,
        "planned_service_life_months": 36,
        "monthly_maintenance": 0.00,
        "required_rental_margin": 0.00,
    },
    "sensitivity": {
        "renewal_rate": 0.0,
        "customer_churn_monthly": 0.0,
        "payment_delay_days": 0,
        "support_overrun_multiplier": 1.0,
        "equipment_replacement_reserve_multiplier": 1.0,
        "downside_scenarios": [],
    },
    "content_capacity": {
        "monthly_assets": 0,
        "revisions": 0,
        "translations": 0,
        "accessibility_checks": 0,
        "support_hours": 0.0,
        "revision_multiplier": 0.5,
        "translation_multiplier": 1.0,
        "accessibility_check_multiplier": 0.5,
        "support_hour_multiplier": 0.25,
        "monthly_capacity_units": 0.0,
    },
    "workforce": {
        "roles": [],
        "subsidy_support_monthly": 0.00,
        "subsidy_end_date": None,
        "funding_independent_continuation_plan": False,
    },
    "evidence_status": "proposed_not_measured",
}
