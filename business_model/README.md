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

The core formula is:

```text
break-even subscriptions = ceil(monthly fixed costs / average monthly contribution)
```

A meaningful result requires a positive average monthly contribution.

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
