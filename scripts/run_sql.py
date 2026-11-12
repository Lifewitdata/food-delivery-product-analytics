"""Run the project SQL locally: BigQuery files in DuckDB, PostgreSQL and Redshift-port files in a real PostgreSQL 16 server."""
from __future__ import annotations

import io
import json
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDERS_CSV = ROOT / "data" / "processed" / "orders_clean_sa.csv"
EVENTS_JSON = ROOT / "data" / "processed" / "events.json"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "reports" / "sql_outputs"
PG_DATA_DIR = Path.home() / ".pg_food_delivery"

# DuckDB has these under other names; the macros let the BigQuery text run unchanged.
BIGQUERY_SHIMS = """
CREATE TYPE float64 AS DOUBLE;
CREATE OR REPLACE MACRO countif(x) AS count_if(x);
CREATE OR REPLACE MACRO safe_divide(a, b) AS CASE WHEN b = 0 THEN NULL ELSE a / b END;
CREATE OR REPLACE MACRO json_value(j, p) AS json_extract_string(j, p);
"""

EVENT_COLUMNS = {
    "order_id": "VARCHAR",
    "customer_id": "VARCHAR",
    "event_type": "VARCHAR",
    "event_time": "TIMESTAMP",
    "device": "VARCHAR",
    "city": "VARCHAR",
    "payload": "JSON",
}


def sql_files(dialect: str) -> list[Path]:
    return sorted(p for p in (SQL_DIR / dialect).glob("0[1-7]_*.sql"))


def duckdb_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("CREATE SCHEMA food_delivery")
    con.execute(
        f"CREATE TABLE food_delivery.orders AS SELECT * FROM read_csv('{ORDERS_CSV.as_posix()}', header = true, "
        "types = {'order_date': 'DATE', 'tip_amount_sar': 'DOUBLE', 'customer_rating': 'DOUBLE', "
        "'delivery_partner_rating': 'DOUBLE'})"
    )
    cols = ", ".join(f"'{k}': '{v}'" for k, v in EVENT_COLUMNS.items())
    con.execute(
        f"CREATE TABLE food_delivery.events AS SELECT * FROM read_json('{EVENTS_JSON.as_posix()}', "
        f"format = 'newline_delimited', columns = {{{cols}}})"
    )
    con.execute(BIGQUERY_SHIMS)
    return con


def run_bigquery_in_duckdb() -> dict[str, pd.DataFrame]:
    con = duckdb_connection()
    return {p.stem: con.execute(p.read_text(encoding="utf-8")).df() for p in sql_files("bigquery")}


def start_postgres():
    import pgserver

    return pgserver.get_server(str(PG_DATA_DIR), cleanup_mode="stop")


def postgres_connection(server, dbname: str = "food_delivery"):
    import psycopg2

    admin = psycopg2.connect(server.get_uri())
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        if cur.fetchone() is None:
            cur.execute(f"CREATE DATABASE {dbname}")
    admin.close()
    return psycopg2.connect(server.get_uri(dbname))


def load_postgres(con) -> dict[str, int]:
    """Create tables from sql/postgres/00_schema.sql and stream both files in with COPY FROM STDIN."""
    orders = pd.read_csv(ORDERS_CSV)
    schema_sql = (SQL_DIR / "postgres" / "00_schema.sql").read_text(encoding="utf-8")
    with con.cursor() as cur:
        cur.execute(schema_sql)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'orders' ORDER BY ordinal_position")
        table_cols = [r[0] for r in cur.fetchall()]
        buf = io.StringIO()
        orders[table_cols].to_csv(buf, index=False)
        buf.seek(0)
        cur.copy_expert(f"COPY orders ({', '.join(table_cols)}) FROM STDIN WITH (FORMAT csv, HEADER true)", buf)

        events = pd.read_json(EVENTS_JSON, lines=True, dtype={"order_id": str})
        events["payload"] = events["payload"].map(json.dumps)
        buf = io.StringIO()
        events[list(EVENT_COLUMNS)].to_csv(buf, index=False)
        buf.seek(0)
        cur.copy_expert(f"COPY events ({', '.join(EVENT_COLUMNS)}) FROM STDIN WITH (FORMAT csv, HEADER true)", buf)

        cur.execute("SELECT COUNT(*) FROM orders")
        n_orders = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events")
        n_events = cur.fetchone()[0]
    con.commit()
    return {"orders": n_orders, "events": n_events}


def run_postgres_dialect(con, dialect: str) -> dict[str, pd.DataFrame]:
    out = {}
    for p in sql_files(dialect):
        with con.cursor() as cur:
            cur.execute(p.read_text(encoding="utf-8"))
            cols = [d[0] for d in cur.description]
            out[p.stem] = pd.DataFrame(cur.fetchall(), columns=cols)
    return out


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Engine-neutral form for comparison: Decimal -> float, sorted rows, plain index."""
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            converted = pd.to_numeric(df[c], errors="coerce")
            if converted.notna().sum() == df[c].notna().sum() and df[c].notna().any():
                df[c] = converted.astype(float)
        elif pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].astype(float)
    return df.sort_values(list(df.columns)).reset_index(drop=True)


def frames_match(a: pd.DataFrame, b: pd.DataFrame, atol: float = 0.011) -> bool:
    a, b = normalise(a), normalise(b)
    if list(a.columns) != list(b.columns) or a.shape != b.shape:
        return False
    try:
        pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=atol, rtol=0)
    except AssertionError:
        return False
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"bigquery_duckdb": run_bigquery_in_duckdb()}

    server = start_postgres()
    con = postgres_connection(server)
    print("PostgreSQL:", con.server_version, "| loaded:", load_postgres(con))
    results["postgres"] = run_postgres_dialect(con, "postgres")
    results["redshift_port_in_postgres"] = run_postgres_dialect(con, "redshift")
    con.close()

    for engine, frames in results.items():
        (OUT_DIR / engine).mkdir(exist_ok=True)
        for name, df in frames.items():
            df.to_csv(OUT_DIR / engine / f"{name}.csv", index=False)

    rows = []
    for name in results["bigquery_duckdb"]:
        rows.append({
            "query": name,
            "rows": len(results["bigquery_duckdb"][name]),
            "bigquery_duckdb_vs_postgres": frames_match(results["bigquery_duckdb"][name], results["postgres"][name]),
            "postgres_vs_redshift_port": frames_match(results["postgres"][name], results["redshift_port_in_postgres"][name]),
        })
    parity = pd.DataFrame(rows)
    parity.to_csv(OUT_DIR / "parity.csv", index=False)
    print(parity.to_string(index=False))
    if not parity[["bigquery_duckdb_vs_postgres", "postgres_vs_redshift_port"]].all().all():
        raise SystemExit("SQL engines disagree - fix the SQL")


if __name__ == "__main__":
    main()
