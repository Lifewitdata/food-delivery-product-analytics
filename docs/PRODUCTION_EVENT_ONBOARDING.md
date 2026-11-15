# Production customer-event data onboarding

## Objective
Replace generated demonstration journeys with an anonymised export from the actual app analytics/event pipeline. This contract does not generate customer behaviour and does not connect to a vendor account.

## Supported export format
CSV, one row per event. Required columns:
- event_id: unique event identifier
- session_id: pseudonymous session identifier
- event_name: canonical event name or an explicitly supported alias
- event_timestamp: ISO-8601 timestamp with timezone, preferably UTC
- platform: ios, android, web, or another documented client
- city: coarse city-level location only

Optional columns:
- customer_id: stable pseudonymous customer/account key; nullable for logged-out users
- anonymous_id: pseudonymous device/browser key; do not send advertising IDs unless lawful and approved
- order_id: pseudonymous order key, populated only for order-related events
- properties_json: JSON object containing approved event properties, never direct identifiers

The canonical event vocabulary is in config/production_event_schema.json. A delivery-completed event is order_delivered, not order_placed; placing an order and completing a delivery are distinct lifecycle events.

## Privacy and security
Never export names, email addresses, phone numbers, precise GPS, full addresses, payment card details, authentication tokens, passwords, or raw support conversations. Use pseudonymous identifiers and minimum necessary properties. Follow the data controller's consent, retention, access-control and deletion policies. Do not commit production customer data to a public Git repository. Keep production exports outside the repository and out of issue comments/logs.

## Validate a supplied export

    python -m scripts.validate_production_events --input /secure/path/events_export.csv

The validator writes:
- data/processed/production_events_validated.csv
- data/processed/production_events_quarantine.csv
- reports/production_event_validation.json

The command exits non-zero if any rows are quarantined. Review and resolve those rows before funnel analysis; do not silently drop them. The default output paths are for local demonstration only. For real customer data, override all output paths to a private, access-controlled location outside the Git checkout.

Example with private output paths:

    python -m scripts.validate_production_events \
      --input /secure/path/events_export.csv \
      --output /secure/output/events_validated.csv \
      --quarantine /secure/output/events_quarantine.csv \
      --summary /secure/output/validation_summary.json

## Funnel event semantics
Recommended event sequence:
1. app_open
2. restaurant_view
3. add_to_cart
4. checkout_started
5. order_placed
6. payment_failed (failure outcome, not a funnel success)
7. order_cancelled (post-order outcome)
8. order_delivered (fulfilment outcome)

The exact tracking plan must be agreed with Product Engineering. Events can repeat (for example multiple restaurant views or cart edits); the production funnel should define first qualifying event per session and a fixed conversion window. Do not infer missing events or create non-buying sessions.

## Source system mapping
Export from the actual source of truth used by the organisation (for example a product analytics platform, mobile/web event collector, or governed warehouse event table). Map its native event names and fields to this contract. Confirm event completeness, consent handling, session timeout definition, identity stitching, timezone, bot/internal traffic exclusion and late-arriving event policy with the data owner.

## What is needed to proceed
A real, anonymised CSV export and the answers to:
- Which system generated it?
- What is the agreed session timeout?
- Is customer_id a stable pseudonymous account key?
- Are timestamps UTC or timezone-offset aware?
- What is the official meaning of each event name?

Until the actual export and definitions are supplied, the repository is only production-ready to accept and validate an export; no genuine customer conversion rate can be calculated.
