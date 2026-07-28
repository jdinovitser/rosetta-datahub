"""
Fiction-Retail data source for Rosetta.

Reads the Kaggle Fiction Retail E-Commerce dataset (fiction_retail.db)
directly from SQLite — no DataHub instance required. Queries real data to
surface genuine quality conflicts that were deliberately planted in the
dataset, then returns MetricDefinition objects that feed the existing
five-agent Rosetta pipeline unchanged.

Dataset: 10 interconnected tables covering orders, customers, products,
inventory, shipments, returns, promotions, warehouses and suppliers.

Key planted conflict:
  • discount_pct unit-convention mismatch:
      – order_items stores 37,161 rows with discount_pct values of 5–30
        (integer percent scale from marketing campaigns)
      – the analytics / catalog team expects decimal fractions 0.0–1.0
      – revenue calculations on those rows are 5–30× overstated in discounts

Pipeline lineage (from add_lineage.py):
    customers + promotions → orders
    orders + products      → order_items
    suppliers              → products
    products + warehouses  → inventory
    orders + warehouses    → shipments
    orders + products      → returns
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .datahub_client import MetricDefinition

_DB_PATH = Path(__file__).resolve().parent.parent / "demo_data" / "fiction_retail.db"

# DataHub-style URNs for the fiction-retail pipeline tables
_PLATFORM = "sqlite"
_ENV = "PROD"
_INSTANCE = "fiction-retail"
_URN = {
    "customers":   f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.customers,{_ENV})",
    "orders":      f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.orders,{_ENV})",
    "order_items": f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.order_items,{_ENV})",
    "products":    f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.products,{_ENV})",
    "promotions":  f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.promotions,{_ENV})",
    "inventory":   f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.inventory,{_ENV})",
    "warehouses":  f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.warehouses,{_ENV})",
    "shipments":   f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.shipments,{_ENV})",
    "returns":     f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.returns,{_ENV})",
    "suppliers":   f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},{_INSTANCE}.suppliers,{_ENV})",
}

# Lineage: each table → its immediate downstream consumers (FK dependencies)
_DOWNSTREAM: dict[str, list[str]] = {
    _URN["customers"]:   [_URN["orders"]],
    _URN["promotions"]:  [_URN["orders"]],
    _URN["orders"]:      [_URN["order_items"], _URN["shipments"], _URN["returns"]],
    _URN["products"]:    [_URN["order_items"], _URN["inventory"], _URN["returns"]],
    _URN["suppliers"]:   [_URN["products"]],
    _URN["warehouses"]:  [_URN["inventory"], _URN["shipments"]],
    _URN["order_items"]: [],
    _URN["inventory"]:   [],
    _URN["shipments"]:   [],
    _URN["returns"]:     [],
}


@dataclass
class _Stats:
    """Real quality counts read from the SQLite database."""
    total_orders: int
    total_items: int
    total_customers: int
    total_products: int
    bad_discount_rows: int       # discount_pct > 1 (integer percent instead of fraction)
    bad_discount_orders: int     # distinct orders affected
    bad_discount_revenue: float  # sum of unit_price * quantity for bad-discount rows
    disc_min: float              # min discount_pct value in bad rows
    disc_max: float              # max discount_pct value in bad rows
    status_values: int           # distinct order_status values
    shipment_state_values: int   # distinct shipment_state values


def _read_stats(conn: sqlite3.Connection) -> _Stats:
    def q(sql: str) -> Any:
        return conn.execute(sql).fetchone()[0]

    return _Stats(
        total_orders=q("SELECT COUNT(*) FROM orders"),
        total_items=q("SELECT COUNT(*) FROM order_items"),
        total_customers=q("SELECT COUNT(*) FROM customers"),
        total_products=q("SELECT COUNT(*) FROM products"),
        bad_discount_rows=q("SELECT COUNT(*) FROM order_items WHERE discount_pct > 1"),
        bad_discount_orders=q("SELECT COUNT(DISTINCT order_id) FROM order_items WHERE discount_pct > 1"),
        bad_discount_revenue=q(
            "SELECT ROUND(SUM(unit_price * quantity), 2) "
            "FROM order_items WHERE discount_pct > 1"
        ) or 0.0,
        disc_min=q("SELECT MIN(discount_pct) FROM order_items WHERE discount_pct > 1") or 0.0,
        disc_max=q("SELECT MAX(discount_pct) FROM order_items WHERE discount_pct > 1") or 0.0,
        status_values=q("SELECT COUNT(DISTINCT order_status) FROM orders"),
        shipment_state_values=q("SELECT COUNT(DISTINCT shipment_state) FROM shipments"),
    )


def _pct(n: int, total: int) -> str:
    return f"{n / total * 100:.1f}%"


def build_metric_definitions(s: _Stats) -> list[MetricDefinition]:
    """
    Return one MetricDefinition per (metric, team) pair.  The Conflict
    Detector compares definitions across teams to find silent contradictions.
    """
    return [

        # ── 1. discount_pct — CRITICAL ───────────────────────────────────────
        # Marketing enters promotions.discount_pct as integer percent (5–50).
        # Commerce/analytics teams read order_items.discount_pct as decimal
        # fraction (0.0–1.0).  37,161 order line items carry integer values
        # from promotions, making downstream revenue calculations 5–30× wrong.
        MetricDefinition(
            name="discount_pct",
            display_name="Discount Percentage",
            domain="commerce_team",
            owner="urn:li:corpGroup:commerce-team",
            definition_text=(
                "Decimal fraction discount applied to a line item at checkout. "
                "Range: 0.0 (no discount) to 1.0 (100% off). "
                "Used to compute net revenue: unit_price × quantity × (1 − discount_pct). "
                "Values outside 0–1 indicate a unit-convention error."
            ),
            sql_logic=(
                "SELECT discount_pct FROM order_items "
                "WHERE discount_pct BETWEEN 0.0 AND 1.0"
            ),
            source_urns=[_URN["order_items"], _URN["orders"]],
            term_urn="urn:li:glossaryTerm:commerce.discount_pct",
            tags=["financial", "pipeline_stage"],
            last_modified="2024-02-14",
        ),
        MetricDefinition(
            name="discount_pct",
            display_name="Discount Percentage",
            domain="marketing_team",
            owner="urn:li:corpGroup:marketing-team",
            definition_text=(
                "Integer percentage discount authored in campaign management tools. "
                "Range: 0 (no discount) to 100 (free). "
                "A value of 20 means 20% off. Stored as-is from the promotions "
                "authoring system — no fractional conversion applied."
            ),
            sql_logic="SELECT discount_pct FROM promotions",
            source_urns=[_URN["promotions"], _URN["order_items"]],
            term_urn="urn:li:glossaryTerm:marketing.discount_pct",
            tags=["financial"],
            last_modified="2023-11-30",
        ),

        # ── 2. order_status / shipment_state — MEDIUM (hidden synonym) ───────
        # commerce_team tracks lifecycle on orders.order_status;
        # logistics_team tracks the same event on shipments.shipment_state.
        # Values are different labels for the same concept — joins and
        # dashboards that mix them silently double-count or miss transitions.
        MetricDefinition(
            name="order_status~shipment_state",
            display_name="Order Status",
            domain="commerce_team",
            owner="urn:li:corpGroup:commerce-team",
            definition_text=(
                "Lifecycle state of an order as tracked by the commerce platform. "
                f"Current distinct values: {s.status_values}. "
                "Used for customer-facing status pages, SLA reporting, and "
                "order management dashboards. Source of truth for order state."
            ),
            sql_logic="SELECT order_status FROM orders",
            source_urns=[_URN["orders"]],
            term_urn="urn:li:glossaryTerm:commerce.order_status",
            tags=["transactional"],
            last_modified="2023-08-10",
        ),
        MetricDefinition(
            name="order_status~shipment_state",
            display_name="Shipment State",
            domain="logistics_team",
            owner="urn:li:corpGroup:logistics-team",
            definition_text=(
                "Current state of a shipment in the carrier pipeline. "
                f"Current distinct values: {s.shipment_state_values}. "
                "Used for carrier tracking, warehouse SLAs, and delivery "
                "exception reporting. Independently updated from order_status — "
                "an order may be marked Delivered while a shipment shows In Transit."
            ),
            sql_logic="SELECT shipment_state FROM shipments",
            source_urns=[_URN["shipments"], _URN["orders"]],
            term_urn="urn:li:glossaryTerm:logistics.shipment_state",
            tags=["transactional"],
            last_modified="2024-01-22",
        ),
    ]


def _transitive_downstream(start_urns: list[str]) -> set[str]:
    """Walk the lineage graph transitively from the given URN(s)."""
    seen: set[str] = set()
    frontier = list(start_urns)
    while frontier:
        node = frontier.pop()
        for child in _DOWNSTREAM.get(node, []):
            if child not in seen:
                seen.add(child)
                frontier.append(child)
    return seen


def _label(urn: str) -> str:
    """Short human label for a URN."""
    name = urn.split(",")[-2] if "," in urn else urn
    return name.split(".")[-1] if "." in name else name


def _kind(urn: str) -> str:
    if "dataset" in urn:
        tbl = urn.split(",")[-2].split(".")[-1] if "," in urn else ""
        if tbl in ("inventory", "returns"):
            return "dashboard"
        return "dataset"
    return "dataset"


class FictionRetailDataSource:
    """
    Drop-in replacement for RosettaDataHub backed by the fiction-retail SQLite DB.

    Implements the same interface used by run_scan() and demo.py:
        harvest_metric_definitions() → list[MetricDefinition]
        downstream_assets(defn)      → set[str]
        impact_graph(defn)           → {"nodes": [...], "edges": [...]}
    """

    def __init__(self) -> None:
        if not _DB_PATH.exists():
            raise FileNotFoundError(
                f"fiction_retail.db not found at {_DB_PATH}. "
                "Download from: https://github.com/datahub-project/static-assets/tree/main/datasets/fiction-retail"
            )
        conn = sqlite3.connect(str(_DB_PATH))
        self._stats = _read_stats(conn)
        conn.close()
        self._definitions = build_metric_definitions(self._stats)

    @property
    def stats(self) -> _Stats:
        return self._stats

    def harvest_metric_definitions(self) -> list[MetricDefinition]:
        for d in self._definitions:
            d.source_urns = list(dict.fromkeys(d.source_urns))
        return self._definitions

    def downstream_assets(self, defn: MetricDefinition) -> set[str]:
        return _transitive_downstream(defn.source_urns)

    def impact_graph(self, defn: MetricDefinition) -> dict:
        origin_id = f"metric::{defn.name}::{defn.domain}"
        nodes: dict[str, dict] = {
            origin_id: {
                "id": origin_id,
                "label": f"{defn.display_name}\n({defn.domain})",
                "type": "metric",
            }
        }
        edges: list[dict] = []
        seen: set[str] = set()
        frontier = list(defn.source_urns)

        for u in frontier:
            if u not in nodes:
                nodes[u] = {"id": u, "label": _label(u), "type": _kind(u)}
            edges.append({"source": origin_id, "target": u})
            seen.add(u)

        while frontier:
            node = frontier.pop()
            for child in _DOWNSTREAM.get(node, []):
                if child not in nodes:
                    nodes[child] = {"id": child, "label": _label(child), "type": _kind(child)}
                edges.append({"source": node, "target": child})
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)

        # dedupe edges
        seen_e: set[tuple] = set()
        deduped = []
        for e in edges:
            k = (e["source"], e["target"])
            if k not in seen_e:
                seen_e.add(k)
                deduped.append(e)

        return {"nodes": list(nodes.values()), "edges": deduped}
