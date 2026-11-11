# Business Model Extension

This module adds an optional recurring-revenue and break-even planning model
to World-HoloBridge.

## Purpose

The module helps evaluate a proposed managed service:

- Holographic display rental.
- Monthly marketing and content service.
- Content updates and campaign management.
- Accessibility and bilingual content support.
- Optional NFC campaign service.
- Optional avatar-service add-on.
- Paid disability-led creative and support roles.

## What it calculates

- Monthly recurring revenue.
- Monthly variable delivery costs.
- Monthly contribution.
- Average contribution per active subscription.
- Break-even subscription count.
- Annualized recurring-revenue run rate.
- Sensitivity: retained revenue after churn, contribution after support
  overrun, payment-delay cash impact, and named downside scenarios.
- Rental recovery: capital to recover, monthly capital recovery, and the
  required monthly rental price.
- Content capacity: workload in asset-equivalent units, capacity
  utilization, and overage.
- Workforce: paid hours, labour and accommodation costs, subsidy support,
  net cost, post-subsidy cost, and continuation risk.

The core formula is:

```text
break-even subscriptions = ceil(monthly fixed costs / average monthly contribution)
```

A meaningful result requires a positive average monthly contribution.

## Sensitivity analysis

Sensitivity parameters are modelled assumptions, not measured customer
behaviour:

- Renewal rate (0–1): share of subscriptions renewing at contract end.
- Monthly customer churn (0–1): share of active customers lost per month.
- Payment delay (days): working capital tied up is roughly
  `monthly recurring revenue * delay_days / 30`. This is a cash-flow
  timing effect, not a profit-and-loss cost.
- Support overrun multiplier: scales only the support-hours variable-cost
  line.
- Equipment replacement reserve multiplier: scales only the risk-reserve
  portion of the rental capital to recover.
- Downside scenarios: named parameter sets (for example `high_churn`) run
  against the same model and report their own contribution and break-even.

## Rental recovery

```text
rental price =
  (equipment landed cost + installation cost + risk reserve)
  / planned service life in months
  + monthly maintenance
  + required rental margin
```

Rental revenue is tracked separately from creative-service revenue. The
template field names follow the formula terms: `risk_reserve` (a lump sum
recovered over the service life), `monthly_maintenance`, and
`required_rental_margin`. Older plan files using `risk_reserve_monthly`,
`maintenance_monthly`, or `required_rental_margin_monthly` are still read.

## Content capacity

Workload is measured in asset-equivalent units:

```text
workload = assets
  + revisions * revision_multiplier
  + translations * translation_multiplier
  + accessibility checks * accessibility_check_multiplier
  + support hours * support_hour_multiplier
```

Default multipliers are transparent planning assumptions: a revision counts
as 0.5 units, a translation as 1.0, an accessibility check as 0.5, and a
support hour as 0.25. Capacity utilization is workload divided by monthly
capacity; above 1.0 the plan is over capacity and the excess is reported
as overage units. A fixed monthly subscription never includes unlimited
content creation: the allowance is defined by asset counts, revisions,
languages, accessibility checks, and support hours, with overage pricing.

## Workforce cost tracking

The model tracks paid roles (name, hours, hourly rate, accommodation),
subsidy support, the subsidy end date, and whether a funding-independent
continuation plan exists. Reported separately:

- Monthly labour cost and accommodation costs.
- Monthly workforce cost (labour plus accommodation).
- Monthly net cost after subsidy support.
- Post-subsidy monthly cost — what the business must carry once the
  subsidy ends.

Subsidy support is restricted funding and is never counted as customer
subscription revenue. When the subsidy covers the full workforce cost and
no continuation plan is recorded, the report flags a continuation risk.

## What it does not claim

This module does **not** establish:

- Measured revenue.
- Verified supplier pricing.
- Proven market demand.
- Guaranteed customer renewal.
- Profitability.
- Solar autonomy.
- Scientific validation of holographic claims.
- Employment outcomes for any worker.

## Evidence rule

A break-even result is a **modelled projection**, not a measured business
result. It becomes decision-grade only when supported by:

- Customer contracts or signed proposals.
- Supplier quotations and specifications.
- Measured delivery, support, and maintenance costs.
- Documented content and accessibility workload.
- Rental, damage, replacement, and financing assumptions.
- A funding-independent workforce plan.
- Renewal and churn data from real customers.
- Payment timing from real invoices.

## Evidence register

The template's `evidence_links` section records, for each new calculation
area, the evidence that would support it. All links start empty: quotes,
supplier specifications, contracts, measured costs, customer feedback,
rental quotes, sensitivity assumptions, content workload logs, and the
workforce plan. A modelled output stays labelled `modelled_not_measured`
until the corresponding evidence is attached.

## Run the report

```bash
python scripts/business_model_report.py business_model/business_model_template.json
```

## Suggested commercial structure

Keep hardware rental, recurring service, custom production, accessibility
work, and workforce support as separately tracked cost and revenue lines.

Do not offer unlimited content creation within a fixed monthly subscription.
Define asset counts, revisions, languages, accessibility checks, support
hours, turnaround times, and overage pricing.
