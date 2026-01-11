from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_DIR = ROOT / "data" / "analytics"
FACT_PATH = ANALYTICS_DIR / "fact_orders.csv"


def main() -> None:
    if not FACT_PATH.exists():
        raise FileNotFoundError(f"Missing {FACT_PATH}. Run scripts/02_prepare_data.py first.")

    df = pd.read_csv(FACT_PATH)

    required = [
        "order_id", "order_date", "orig_port_cd", "dest_port_cd", "carrier",
        "mode_dsc", "is_on_time", "is_late", "ship_late_day_count",
        "freight_cost_est", "unit_quantity", "weight", "daily_capacity", "wh_cost_per_unit"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"fact_orders.csv missing required columns: {missing}")

    # Types
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["freight_cost_est"] = pd.to_numeric(df["freight_cost_est"], errors="coerce").fillna(0)
    df["ship_late_day_count"] = pd.to_numeric(df["ship_late_day_count"], errors="coerce").fillna(0)
    df["unit_quantity"] = pd.to_numeric(df["unit_quantity"], errors="coerce").fillna(0)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0)
    df["daily_capacity"] = pd.to_numeric(df["daily_capacity"], errors="coerce")
    df["wh_cost_per_unit"] = pd.to_numeric(df["wh_cost_per_unit"], errors="coerce")

    # Lane key
    df["lane"] = df["orig_port_cd"].astype(str) + " → " + df["dest_port_cd"].astype(str)

    # -----------------------------------
    # 1) SLA layer (rule-based targets)
    # -----------------------------------
    # You can tune these later for your story
    SLA_TARGET_BY_MODE = {"AIR": 0.99, "SEA": 0.95, "TRUCK": 0.97, "RAIL": 0.96}
    df["sla_target"] = df["mode_dsc"].map(SLA_TARGET_BY_MODE).fillna(0.97)

    kpi_sla = (
        df.groupby(["mode_dsc", "carrier", "lane"], dropna=False)
          .agg(
              orders=("order_id", "count"),
              on_time_rate=("is_on_time", "mean"),
              late_rate=("is_late", "mean"),
              avg_late_days=("ship_late_day_count", "mean"),
              total_freight_cost=("freight_cost_est", "sum"),
              sla_target=("sla_target", "mean"),
          )
          .reset_index()
    )
    kpi_sla["sla_breach_pp"] = ((kpi_sla["sla_target"] - kpi_sla["on_time_rate"]) * 100).clip(lower=0)
    kpi_sla["sla_score"] = (kpi_sla["on_time_rate"] / kpi_sla["sla_target"]).clip(upper=1.25)
    kpi_sla.to_csv(ANALYTICS_DIR / "kpi_sla.csv", index=False)

    # -----------------------------------
    # 2) Risk scoring (derived from your data)
    # -----------------------------------
    # Risk components:
    # - Lane late rate
    # - Carrier late rate
    # - Late severity (late days)
    # - Cost scaled
    lane_late = df.groupby("lane")["is_late"].mean()
    carrier_late = df.groupby("carrier")["is_late"].mean()

    df["lane_late_rate"] = df["lane"].map(lane_late).fillna(df["is_late"].mean())
    df["carrier_late_rate"] = df["carrier"].map(carrier_late).fillna(df["is_late"].mean())

    # Mode risk factor: keep it lightweight
    MODE_RISK = {"AIR": 0.25, "SEA": 0.60, "TRUCK": 0.40, "RAIL": 0.50}
    df["mode_risk"] = df["mode_dsc"].map(MODE_RISK).fillna(0.40)

    cost = df["freight_cost_est"].astype(float)
    cost_scaled = (cost - cost.min()) / (cost.max() - cost.min() + 1e-9)
    df["cost_scaled"] = cost_scaled

    late_days = df["ship_late_day_count"].astype(float)
    late_days_scaled = (late_days - late_days.min()) / (late_days.max() - late_days.min() + 1e-9)
    df["late_days_scaled"] = late_days_scaled

    df["risk_score"] = (
        100 * (
            0.35 * df["lane_late_rate"]
            + 0.30 * df["carrier_late_rate"]
            + 0.20 * df["late_days_scaled"]
            + 0.10 * df["cost_scaled"]
            + 0.05 * df["mode_risk"]
        )
    ).clip(0, 100)

    df["risk_band"] = pd.cut(df["risk_score"], [-1, 33, 66, 101], labels=["Low", "Medium", "High"])

    risk_shipments = df[
        ["order_id", "order_date", "lane", "orig_port_cd", "dest_port_cd", "carrier", "mode_dsc",
         "is_on_time", "is_late", "ship_late_day_count", "freight_cost_est", "risk_score", "risk_band"]
    ].copy()
    risk_shipments.to_csv(ANALYTICS_DIR / "risk_shipments.csv", index=False)

    # -----------------------------------
    # 3) Exceptions queue (what ops teams work from)
    # -----------------------------------
    late_df = df[df["is_late"] == True].copy()
    if late_df.empty:
        exceptions = pd.DataFrame(columns=["order_id","order_date","lane","carrier","mode_dsc","ship_late_day_count","freight_cost_est","risk_score","priority_score"])
    else:
        late_df["priority_score"] = (0.65 * late_df["risk_score"] + 0.35 * (late_df["cost_scaled"] * 100)).clip(0, 100)
        exceptions = (
            late_df.sort_values("priority_score", ascending=False)
                   .head(50)[
                       ["order_id","order_date","lane","carrier","mode_dsc","ship_late_day_count","freight_cost_est","risk_score","risk_band","priority_score"]
                   ]
        )
    exceptions.to_csv(ANALYTICS_DIR / "exceptions.csv", index=False)

    # -----------------------------------
    # 4) Seasonality (monthly trends)
    # -----------------------------------
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    seasonality = (
        df.groupby("month", dropna=False)
          .agg(
              orders=("order_id", "count"),
              on_time_rate=("is_on_time", "mean"),
              late_rate=("is_late", "mean"),
              avg_late_days=("ship_late_day_count", "mean"),
              total_freight_cost=("freight_cost_est", "sum"),
              avg_freight_cost=("freight_cost_est", "mean"),
          )
          .reset_index()
          .sort_values("month")
    )
    seasonality["seasonality_index_orders"] = seasonality["orders"] / (seasonality["orders"].mean() + 1e-9)
    seasonality.to_csv(ANALYTICS_DIR / "seasonality_monthly.csv", index=False)

    # -----------------------------------
    # 5) Margin-at-risk proxy (consistent, explainable)
    # -----------------------------------
    # We do NOT invent "real revenue". We proxy order value from freight cost as % of value.
    MODE_FREIGHT_PCT = {"AIR": 0.06, "SEA": 0.03, "TRUCK": 0.04, "RAIL": 0.035}
    df["freight_pct_of_value"] = df["mode_dsc"].map(MODE_FREIGHT_PCT).fillna(0.04)
    df["order_value_proxy"] = df["freight_cost_est"] / df["freight_pct_of_value"]

    # margin % by carrier_type for stability (avoids random per-row noise)
    rng = np.random.default_rng(42)
    ct_list = sorted(df["carrier_type"].dropna().unique().tolist())
    margin_map = {ct: float(rng.uniform(0.18, 0.35)) for ct in ct_list}
    df["margin_pct"] = df["carrier_type"].map(margin_map).fillna(0.25)

    df["gross_margin_proxy"] = df["order_value_proxy"] * df["margin_pct"]
    df["margin_at_risk"] = df["gross_margin_proxy"] * df["is_late"].astype(int)

    kpi_mar = (
        df.groupby(["mode_dsc", "lane", "carrier"], dropna=False)
          .agg(
              orders=("order_id", "count"),
              late_rate=("is_late", "mean"),
              total_freight_cost=("freight_cost_est", "sum"),
              total_order_value_proxy=("order_value_proxy", "sum"),
              total_margin_proxy=("gross_margin_proxy", "sum"),
              total_margin_at_risk=("margin_at_risk", "sum"),
          )
          .reset_index()
    )
    kpi_mar["margin_at_risk_pct"] = kpi_mar["total_margin_at_risk"] / (kpi_mar["total_margin_proxy"] + 1e-9)
    kpi_mar.to_csv(ANALYTICS_DIR / "kpi_margin_at_risk.csv", index=False)

    # -----------------------------------
    # 6) Inventory risk proxy (warehouse cost + capacity + volume)
    # -----------------------------------
    # We don't have warehouse_id; we proxy "node" using plant_code + dest_port_cd.
    df["node"] = df["plant_code"].astype(str) + " @ " + df["dest_port_cd"].astype(str)

    node = (
        df.groupby("node", dropna=False)
          .agg(
              orders=("order_id", "count"),
              avg_daily_capacity=("daily_capacity", "mean"),
              avg_wh_cost_per_unit=("wh_cost_per_unit", "mean"),
              avg_unit_qty=("unit_quantity", "mean"),
              avg_weight=("weight", "mean"),
              late_rate=("is_late", "mean"),
          )
          .reset_index()
    )

    # Risk score: demand pressure vs capacity + late rate + warehouse cost
    demand_scaled = (node["orders"] - node["orders"].min()) / (node["orders"].max() - node["orders"].min() + 1e-9)
    cap = node["avg_daily_capacity"].fillna(node["avg_daily_capacity"].median())
    cap_scaled = (cap - cap.min()) / (cap.max() - cap.min() + 1e-9)
    whc = node["avg_wh_cost_per_unit"].fillna(node["avg_wh_cost_per_unit"].median())
    whc_scaled = (whc - whc.min()) / (whc.max() - whc.min() + 1e-9)

    node["inventory_risk_score"] = (100 * (0.45 * demand_scaled + 0.30 * (1 - cap_scaled) + 0.15 * whc_scaled + 0.10 * node["late_rate"])).clip(0, 100)
    node["inventory_risk_band"] = pd.cut(node["inventory_risk_score"], [-1, 33, 66, 101], labels=["Low", "Medium", "High"])
    node.to_csv(ANALYTICS_DIR / "inventory_risk.csv", index=False)

    # -----------------------------------
    # 7) Scenarios table (simple exec what-if)
    # -----------------------------------
    baseline_cost = float(df["freight_cost_est"].sum())
    baseline_on_time = float(df["is_on_time"].mean())

    scenarios = pd.DataFrame(
        [
            ("Baseline", 0.00, 0.00, baseline_cost, baseline_on_time),
            ("Fuel +10% (cost +7%)", 0.10, 0.00, baseline_cost * 1.07, baseline_on_time),
            ("Port congestion +20% (OT -2pp)", 0.00, 0.20, baseline_cost * 1.01, max(0.0, baseline_on_time - 0.02)),
            ("Capacity constraint (OT -1pp, cost +3%)", 0.00, 0.00, baseline_cost * 1.03, max(0.0, baseline_on_time - 0.01)),
        ],
        columns=["scenario", "fuel_increase", "port_congestion", "total_freight_cost_est", "on_time_rate_est"]
    )
    scenarios.to_csv(ANALYTICS_DIR / "scenarios.csv", index=False)

    print("Wrote v2 control tower tables to data/analytics/")


if __name__ == "__main__":
    main()
