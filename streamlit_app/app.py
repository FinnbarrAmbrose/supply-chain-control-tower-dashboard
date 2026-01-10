from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Supply Chain Control Tower", layout="wide")

BASE = Path(__file__).resolve().parents[1]
ANALYTICS = BASE / "data" / "analytics"

FACT = ANALYTICS / "fact_orders.csv"
KPI_DAILY = ANALYTICS / "kpi_daily.csv"
KPI_LANE = ANALYTICS / "kpi_lane.csv"
KPI_CARRIER = ANALYTICS / "kpi_carrier.csv"
KPI_PLANT = ANALYTICS / "kpi_plant.csv"

st.title("Supply Chain Control Tower")

missing = [p for p in [FACT, KPI_DAILY, KPI_LANE, KPI_CARRIER, KPI_PLANT] if not p.exists()]
if missing:
    st.error("Missing analytics files. Run: python scripts/02_prepare_data.py")
    st.write("Missing:", [str(p) for p in missing])
    st.stop()

fact = pd.read_csv(FACT, parse_dates=["order_date"])
daily = pd.read_csv(KPI_DAILY)
lane = pd.read_csv(KPI_LANE)
carrier = pd.read_csv(KPI_CARRIER)
plant = pd.read_csv(KPI_PLANT)

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

svc_sel = st.sidebar.multiselect("Service level", sorted(f["svc_cd"].dropna().unique().tolist()))
if svc_sel:
    f = f[f["svc_cd"].isin(svc_sel)]

# ---------------- KPI tiles ----------------
c1, c2, c3, c4, c5 = st.columns(5)

orders = f["order_id"].nunique()
units = float(f["unit_quantity"].fillna(0).sum())
late = int(f["is_late"].fillna(False).sum())
on_time_rate = float(f["is_on_time"].fillna(False).mean()) if len(f) else 0.0
freight_cost = float(f["freight_cost_est"].fillna(0).sum())

c1.metric("Orders", f"{orders:,}")
c2.metric("Units", f"{units:,.0f}")
c3.metric("Late orders", f"{late:,}")
c4.metric("On-time rate", f"{on_time_rate:.1%}")
c5.metric("Est. freight cost", f"{freight_cost:,.0f}")

st.divider()

# ---------------- Charts ----------------
st.subheader("Orders over time")
ts = (
    f.groupby(f["order_date"].dt.date)
    .agg(orders=("order_id", "nunique"), freight_cost=("freight_cost_est", "sum"))
    .reset_index()
    .rename(columns={"order_date": "date"})
)
st.line_chart(ts.set_index("date")[["orders"]])

st.subheader("Top lanes by estimated freight cost")
lane_cost = (
    f.groupby(["orig_port_cd", "dest_port_cd"])
    .agg(freight_cost=("freight_cost_est", "sum"), orders=("order_id", "nunique"))
    .reset_index()
    .sort_values("freight_cost", ascending=False)
    .head(15)
)
st.dataframe(lane_cost, width="stretch")

st.subheader("Carrier performance (top 15 by orders)")
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
)
st.dataframe(carrier_perf, width="stretch")

st.subheader("Plant throughput and capacity proxy (top 15 by units)")
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
plant_perf = plant_perf.sort_values("units", ascending=False).head(15)
st.dataframe(plant_perf, width="stretch")

st.divider()
st.subheader("Data preview (fact_orders)")
st.dataframe(f.head(50), width="stretch")
