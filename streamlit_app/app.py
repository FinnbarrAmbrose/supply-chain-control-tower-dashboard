from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Supply Chain Control Tower", layout="wide")

# ---------------- Paths ----------------
BASE = Path(__file__).resolve().parents[1]
ANALYTICS = BASE / "data" / "analytics"
FACT = ANALYTICS / "fact_orders.csv"

# ---------------- Friendly labels ----------------
FRIENDLY = {
    "order_id": "Order ID",
    "order_date": "Order Date",
    "orig_port_cd": "Origin Port",
    "dest_port_cd": "Destination Port",
    "carrier": "Carrier",
    "svc_cd": "Service Code",
    "tpt": "Transit Time (days)",
    "ship_late_day_count": "Days Late",
    "ship_ahead_day_count": "Days Early",
    "unit_quantity": "Units",
    "freight_cost_est": "Estimated Freight Cost",
    "mode_dsc": "Mode",
    "carrier_type": "Carrier Type",
    "plant_code": "Plant",
    "daily_capacity": "Daily Capacity",
    "wh_cost_per_unit": "Warehouse Cost / Unit",
    "customer": "Customer",
    "product_id": "Product ID",
    "weight": "Weight",
}

# ---------------- Formatting helpers ----------------
def fmt_compact(n: float) -> str:
    try:
        n = float(n)
        if abs(n) >= 1_000_000_000:
            return f"{n/1_000_000_000:.1f}B"
        if abs(n) >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if abs(n) >= 1_000:
            return f"{n/1_000:.1f}k"
        return f"{n:.0f}"
    except Exception:
        return "—"

def fmt_pct(x: float) -> str:
    try:
        return f"{float(x):.1%}"
    except Exception:
        return "—"

def to_date_range(df: pd.DataFrame) -> str:
    if df.empty:
        return "—"
    return f"{df['order_date'].min().date()} to {df['order_date'].max().date()}"

def status_badge(label: str, ok: bool, warn: bool = False) -> str:
    # Streamlit markdown badge
    if ok:
        return f"✅ {label}"
    if warn:
        return f"⚠ {label}"
    return f"❌ {label}"

# ---------------- Load ----------------
st.title("Supply Chain Control Tower")
st.caption("Operations-first control tower: service performance, exceptions, and operational risk drivers.")

if not FACT.exists():
    st.error("Missing analytics files. Run: python scripts/02_prepare_data.py")
    st.stop()

fact = pd.read_csv(FACT, parse_dates=["order_date"])

# ---------------- Definitions / assumptions ----------------
with st.expander("Definitions, assumptions, and limitations", expanded=False):
    st.markdown(
        """
**Definitions**
- **Lane**: Origin Port → Destination Port  
- **Carrier**: shipping provider code used on a lane  
- **Service Code**: carrier-provided service tier code (e.g., CRF/DTD/DTP)  
- **Late order**: `Days Late > 0`  
- **Estimated Freight Cost**: `max(minimum_cost, weight * rate)` after matching to the rate card by lane + carrier + service code + weight band.

**Limitations**
- This public dataset appears to be a snapshot with limited date range, so time-series trend analysis may be limited.
        """
    )

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

min_date = fact["order_date"].min().date()
max_date = fact["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", (min_date, max_date))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask = (fact["order_date"].dt.date >= start) & (fact["order_date"].dt.date <= end)
    f = fact.loc[mask].copy()
else:
    f = fact.copy()

carrier_sel = st.sidebar.multiselect("Carrier", sorted(f["carrier"].dropna().unique().tolist()))
if carrier_sel:
    f = f[f["carrier"].isin(carrier_sel)]

svc_sel = st.sidebar.multiselect("Service Code", sorted(f["svc_cd"].dropna().unique().tolist()))
if svc_sel:
    f = f[f["svc_cd"].isin(svc_sel)]

st.sidebar.divider()
st.sidebar.caption("Tip: Use filters to isolate a carrier/service and see how risk drivers change.")

# ---------------- Targets (tune later) ----------------
TARGET_ON_TIME = 0.98          # 98%
TARGET_LATE_RATE = 0.02        # 2% late or less
# Freight cost/order has no true unit; treat as internal KPI for comparison
# We'll set a "soft" threshold using baseline (overall) so it's never arbitrary.

# ---------------- Executive Summary ----------------
st.subheader("Executive summary (scan-and-decide)")

orders = int(f["order_id"].nunique())
units = float(f["unit_quantity"].fillna(0).sum())
late_orders = int(f["is_late"].fillna(False).sum())
on_time_rate = float(f["is_on_time"].fillna(False).mean()) if len(f) else 0.0
freight_cost = float(f["freight_cost_est"].fillna(0).sum())

late_rate = (late_orders / orders) if orders else 0.0
cost_per_order = (freight_cost / orders) if orders else 0.0
avg_tpt = float(f["tpt"].dropna().mean()) if len(f) else 0.0

# Baseline cost/order (all data) for a soft comparator
base_orders = int(fact["order_id"].nunique())
base_cost = float(fact["freight_cost_est"].fillna(0).sum())
base_cost_per_order = (base_cost / base_orders) if base_orders else 0.0

# Status rules
on_time_ok = on_time_rate >= TARGET_ON_TIME
on_time_warn = (TARGET_ON_TIME - 0.01) <= on_time_rate < TARGET_ON_TIME

late_ok = late_rate <= TARGET_LATE_RATE
late_warn = TARGET_LATE_RATE < late_rate <= (TARGET_LATE_RATE + 0.01)

cost_ok = cost_per_order <= (base_cost_per_order * 1.10)  # within +10% of baseline
cost_warn = (base_cost_per_order * 1.10) < cost_per_order <= (base_cost_per_order * 1.25)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Orders", fmt_compact(orders))
c2.metric("Late orders", fmt_compact(late_orders))
c3.metric("Late rate", fmt_pct(late_rate))
c4.metric("On-time rate", fmt_pct(on_time_rate))
c5.metric("Est. freight cost", fmt_compact(freight_cost))
c6.metric("Cost / order", f"{cost_per_order:,.2f}")

st.caption(f"Data range in view: {to_date_range(f)}")

# Clear "status line" for humans
status_line = " | ".join([
    status_badge(f"On-time ≥ {TARGET_ON_TIME:.0%}", on_time_ok, on_time_warn),
    status_badge(f"Late rate ≤ {TARGET_LATE_RATE:.0%}", late_ok, late_warn),
    status_badge("Cost/order vs baseline", cost_ok, cost_warn),
])
st.markdown(f"**Status:** {status_line}")

# A short "what to look at first" message
st.markdown("**What to look at first:** 1) Worst carriers by on-time, 2) Highest-risk lanes, 3) Late orders with high days-late or high cost exposure.")
st.divider()

# ---------------- HERO CHARTS (drivers) ----------------
st.subheader("Drivers (what is causing the issues?)")

h1, h2, h3 = st.columns(3)

# 1) Worst carriers by on-time (volume filtered)
with h1:
    st.markdown("**Worst carriers by on-time rate (top by volume)**")
    carrier_stats = (
        f.groupby("carrier")
         .agg(
            orders=("order_id", "nunique"),
            on_time_rate=("is_on_time", "mean"),
            freight_cost=("freight_cost_est", "sum"),
         )
         .reset_index()
    )
    carrier_stats = carrier_stats[carrier_stats["orders"] >= 50].copy()
    if carrier_stats.empty:
        st.info("Not enough volume to rank carriers under current filters.")
    else:
        worst = carrier_stats.sort_values(["on_time_rate", "orders"], ascending=[True, False]).head(10)
        st.bar_chart(worst.set_index("carrier")[["on_time_rate"]])
        st.caption("Lower bars = worse service performance.")

# 2) Highest-risk lanes (cost × service failure)
with h2:
    st.markdown("**Highest-risk lanes (cost × (1 − on-time))**")
    lane_risk = (
        f.groupby(["orig_port_cd", "dest_port_cd"])
         .agg(
            orders=("order_id", "nunique"),
            freight_cost=("freight_cost_est", "sum"),
            on_time_rate=("is_on_time", "mean"),
         )
         .reset_index()
    )
    lane_risk = lane_risk[lane_risk["orders"] >= 20].copy()
    if lane_risk.empty:
        st.info("Not enough lane volume to compute risk under current filters.")
    else:
        lane_risk["risk_score"] = lane_risk["freight_cost"] * (1 - lane_risk["on_time_rate"])
        lane_risk["lane"] = lane_risk["orig_port_cd"] + " → " + lane_risk["dest_port_cd"]
        top_risk = lane_risk.sort_values("risk_score", ascending=False).head(10)
        st.bar_chart(top_risk.set_index("lane")[["risk_score"]])
        st.caption("Higher bars = higher combined cost + service risk.")

# 3) Cost concentration (top lanes by cost)
with h3:
    st.markdown("**Cost concentration (top lanes by freight cost)**")
    lane_cost = (
        f.groupby(["orig_port_cd", "dest_port_cd"])
         .agg(freight_cost=("freight_cost_est", "sum"))
         .reset_index()
    )
    if lane_cost.empty:
        st.info("No data under current filters.")
    else:
        lane_cost["lane"] = lane_cost["orig_port_cd"] + " → " + lane_cost["dest_port_cd"]
        top_cost = lane_cost.sort_values("freight_cost", ascending=False).head(10)
        st.bar_chart(top_cost.set_index("lane")[["freight_cost"]])
        st.caption("Higher bars = more spend concentrated on that lane.")

st.divider()

# ---------------- ACTION PANEL (exceptions) ----------------
st.subheader("Action list (what needs attention today?)")

late_df = f[f["is_late"] == True].copy()
if late_df.empty:
    st.info("No late orders in the current filter selection.")
else:
    # A readable top-25 action list
    late_df["cost_exposure"] = late_df["freight_cost_est"].fillna(0)
    late_df = late_df.sort_values(["ship_late_day_count", "cost_exposure"], ascending=[False, False])

    action_cols = [
        "order_id", "order_date", "customer", "plant_code",
        "orig_port_cd", "dest_port_cd", "carrier", "svc_cd",
        "ship_late_day_count", "tpt", "weight", "freight_cost_est"
    ]

    top25 = late_df[action_cols].head(25).rename(columns=FRIENDLY)
    st.dataframe(top25, width="stretch")
    st.caption("Top 25 late orders ranked by Days Late (then cost exposure).")

    # Late severity distribution
    st.markdown("**Late severity distribution (Days Late)**")
    late_days = late_df["ship_late_day_count"].fillna(0).astype(int).clip(lower=0, upper=14)
    dist = late_days.value_counts().sort_index().reset_index()
    dist.columns = ["days_late", "orders"]
    dist["days_late"] = dist["days_late"].astype(str)
    st.bar_chart(dist.set_index("days_late")[["orders"]])

    with st.expander("Full late orders list + download", expanded=False):
        full_view = late_df[action_cols].rename(columns=FRIENDLY)
        st.dataframe(full_view.head(200), width="stretch")
        st.download_button(
            "Download late orders CSV",
            data=full_view.to_csv(index=False).encode("utf-8"),
            file_name="late_orders.csv",
            mime="text/csv",
        )

st.divider()

# ---------------- SUPPORTING TABLES (kept, but not dominant) ----------------
with st.expander("Supporting tables (optional)", expanded=False):

    st.markdown("**Carrier performance (top 15 by orders)**")
    carrier_perf = (
        f.groupby(["carrier", "mode_dsc", "carrier_type"])
         .agg(
            orders=("order_id", "nunique"),
            freight_cost=("freight_cost_est", "sum"),
            on_time_rate=("is_on_time", "mean"),
            avg_tpt=("tpt", "mean"),
         )
         .reset_index()
         .sort_values("orders", ascending=False)
         .head(15)
         .rename(columns={
             "carrier": "Carrier",
             "mode_dsc": "Mode",
             "carrier_type": "Carrier Type",
             "orders": "Orders",
             "freight_cost": "Estimated Freight Cost",
             "on_time_rate": "On-time rate",
             "avg_tpt": "Avg Transit Time (days)",
         })
    )
    st.dataframe(carrier_perf, width="stretch")

    st.markdown("**Plant throughput and capacity proxy (top 15 by units)**")
    plant_perf = (
        f.groupby("plant_code")
         .agg(
            orders=("order_id", "nunique"),
            units=("unit_quantity", "sum"),
            avg_daily_capacity=("daily_capacity", "mean"),
         )
         .reset_index()
    )
    plant_perf["capacity_util_proxy"] = plant_perf["units"] / (plant_perf["avg_daily_capacity"] * 30)
    plant_perf = (
        plant_perf.sort_values("units", ascending=False)
        .head(15)
        .rename(columns={
            "plant_code": "Plant",
            "orders": "Orders",
            "units": "Units",
            "avg_daily_capacity": "Avg Daily Capacity",
            "capacity_util_proxy": "Capacity util (proxy)",
        })
    )
    st.dataframe(plant_perf, width="stretch")

# ---------------- Data preview ----------------
with st.expander("Data preview (fact_orders)", expanded=False):
    preview_cols = [
        "order_id", "order_date", "customer", "product_id",
        "plant_code", "orig_port_cd", "dest_port_cd",
        "carrier", "svc_cd", "tpt",
        "unit_quantity", "weight", "freight_cost_est",
        "ship_late_day_count", "ship_ahead_day_count",
    ]
    st.dataframe(f[preview_cols].head(50).rename(columns=FRIENDLY), width="stretch")
