"""Build a labelled synthetic session/event layer for funnel analysis.

The source pack contains one completed journey per order. This generator adds
non-converting sessions without changing source orders or misrepresenting data
as observed production behaviour.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORDERS = ROOT / "data" / "processed" / "orders_clean_sa.csv"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "product_sessions.csv"
DEFAULT_SEED = 2026
FUNNEL = ["app_open", "restaurant_view", "add_to_cart", "checkout_started", "order_placed"]

def build_sessions(orders: pd.DataFrame, seed: int = DEFAULT_SEED,
                   non_converting_sessions_per_customer: float = 2.0) -> pd.DataFrame:
    """Return event-grain rows; generated non-purchase journeys are labelled synthetic."""
    required = {"order_id", "customer_id", "city", "device", "order_datetime"}
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f"Orders are missing required columns: {sorted(missing)}")
    if non_converting_sessions_per_customer < 0:
        raise ValueError("non_converting_sessions_per_customer must be >= 0")
    rng = np.random.default_rng(seed)
    source = orders.copy()
    source["order_datetime"] = pd.to_datetime(source["order_datetime"], errors="coerce")
    if source["order_datetime"].isna().any():
        raise ValueError("order_datetime contains missing or invalid values")
    events = []

    def append_journey(session_id, customer_id, city, device, started_at,
                       event_names, order_id, provenance):
        for position, event_name in enumerate(event_names):
            events.append({
                "session_id": session_id, "customer_id": customer_id,
                "city": city, "device": device, "event_name": event_name,
                "event_timestamp": started_at + pd.Timedelta(minutes=int(position * rng.integers(1, 4))),
                "event_sequence": position + 1, "order_id": order_id,
                "converted": event_name == "order_placed",
                "data_provenance": provenance,
            })

    for row in source.itertuples(index=False):
        append_journey(f"ORDER-{row.order_id}", str(row.customer_id), str(row.city),
                       str(row.device), row.order_datetime - pd.Timedelta(minutes=15),
                       FUNNEL, str(row.order_id), "source_order_journey_synthetic_events")

    customers = source.groupby("customer_id", sort=True).agg(
        city=("city", "first"), device=("device", "first"),
        first_seen=("order_datetime", "min")).reset_index()
    n_extra = int(round(len(customers) * non_converting_sessions_per_customer))
    stage_weights = np.array([0.12, 0.28, 0.35, 0.25])
    for idx in range(n_extra):
        customer = customers.iloc[int(rng.integers(0, len(customers)))]
        depth = int(rng.choice(np.arange(1, 5), p=stage_weights))
        start = customer["first_seen"] - pd.Timedelta(days=int(rng.integers(1, 45)))
        start += pd.Timedelta(minutes=int(rng.integers(0, 1440)))
        append_journey(f"NONBUYER-{seed}-{idx:07d}", str(customer.customer_id),
                       str(customer.city), str(customer.device), start,
                       FUNNEL[:depth], None, "synthetic_non_converting_session")
    return pd.DataFrame(events).sort_values(
        ["session_id", "event_sequence"], kind="stable").reset_index(drop=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=Path, default=DEFAULT_ORDERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--extra-sessions-per-customer", type=float, default=2.0)
    args = parser.parse_args()
    orders = pd.read_csv(args.orders, parse_dates=["order_datetime"])
    sessions = build_sessions(orders, args.seed, args.extra_sessions_per_customer)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sessions.to_csv(args.output, index=False)
    summary = sessions.groupby("event_name").session_id.nunique().reindex(FUNNEL, fill_value=0)
    print(f"Wrote {len(sessions):,} event rows across {sessions.session_id.nunique():,} sessions")
    print("Session counts by event:")
    print(summary.to_string())
    print("NOTE: non-converting sessions are simulated, not observed production traffic.")

if __name__ == "__main__":
    main()
