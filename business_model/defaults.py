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
    "evidence_status": "proposed_not_measured",
}
