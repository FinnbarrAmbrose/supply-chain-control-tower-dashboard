# streamlit_app/app.py
from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

# Plotly template is set dynamically after the theme toggle



# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Supply Chain Control Tower",
    page_icon="📦",
    layout="wide",
)

# =========================
# Theme toggle (Dark / Light)
# =========================
st.sidebar.markdown("## Control Panel")
theme_mode = st.sidebar.toggle("Dark mode", value=True)

PLOTLY_TEMPLATE = "plotly_dark" if theme_mode else "plotly_white"
px.defaults.template = PLOTLY_TEMPLATE

# =========================
# Theme variables (ONE source of truth)
# =========================
if theme_mode:
    css_vars = {
        "--bg": "#07101f",
        "--panel": "#0b162a",
        "--panel2": "rgba(255,255,255,0.06)",
        "--text": "rgba(255,255,255,0.92)",
        "--muted": "rgba(255,255,255,0.62)",
        "--border": "rgba(148,163,184,0.20)",
        "--shadow": "0 12px 30px rgba(0,0,0,0.38)",
        "--primary": "#3b82f6",

        # status
        "--ok": "#22c55e",
        "--warn": "#f59e0b",
        "--bad": "#ef4444",

        # code (inline + blocks)
        "--code_bg": "#0f1d36",
        "--code_text": "rgba(255,255,255,0.92)",

        # controls (closed select)
        "--control_bg": "rgba(255,255,255,0.06)",
        "--control_text": "rgba(255,255,255,0.92)",

        # menu (opened dropdown) -> force readable (white background + dark text)
        "--menu_bg": "#ffffff",
        "--menu_text": "#0f172a",
    }
else:
    css_vars = {
        "--bg": "#f6f8fb",
        "--panel": "#ffffff",
        "--panel2": "#f1f5f9",
        "--text": "#0f172a",
        "--muted": "rgba(15,23,42,0.62)",
        "--border": "rgba(15,23,42,0.10)",
        "--shadow": "0 10px 22px rgba(2,6,23,0.08)",
        "--primary": "#2563eb",

        # status
        "--ok": "#16a34a",
        "--warn": "#d97706",
        "--bad": "#dc2626",

        # code (inline + blocks)
        "--code_bg": "#f1f5f9",
        "--code_text": "#0f172a",

        # controls (closed select)
        "--control_bg": "#ffffff",
        "--control_text": "#0f172a",

        # menu (opened dropdown)
        "--menu_bg": "#ffffff",
        "--menu_text": "#0f172a",
    }

css_vars_block = "\n".join([f"  {k}: {v};" for k, v in css_vars.items()])

# =========================
# CSS (enterprise UI + FIXES)
# =========================
st.markdown(
    f"""
<style>
:root {{
{css_vars_block}
}}

/* ===== App background ===== */
html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important;
  color: var(--text) !important;
}}

/* ===== Remove the “white bar” / Streamlit chrome ===== */
header[data-testid="stHeader"] {{
  background: transparent !important;
}}
[data-testid="stDecoration"] {{
  background: transparent !important;
}}
[data-testid="stToolbar"] {{
  background: transparent !important;
}}

/* ===== Layout ===== */
.block-container {{
  padding-top: 1.2rem;
  padding-bottom: 1.2rem;
  max-width: 1400px;
}}

h1, h2, h3, p, li, label, span, div {{
  color: var(--text);
}}

small, .stCaption, [data-testid="stCaptionContainer"] {{
  color: var(--muted) !important;
}}

hr {{
  border-color: var(--border) !important;
}}

/* ===== Cards ===== */
.dashboard-card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: var(--shadow);
}}

.card-title {{
  color: var(--muted);
  font-size: 0.85rem;
  margin-bottom: 6px;
}}

.card-value {{
  font-size: 1.60rem;
  font-weight: 760;
  color: var(--text);
}}

.card-sub {{
  color: var(--muted);
  font-size: 0.80rem;
  margin-top: 8px;
}}

.section-card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}}

.section-title {{
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 10px;
}}

/* ===== Pills ===== */
.pill {{
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  margin-right: 8px;
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--text);
}}
.pill-ok {{ background: rgba(34,197,94,0.14); }}
.pill-warn {{ background: rgba(245,158,11,0.14); }}
.pill-bad {{ background: rgba(239,68,68,0.14); }}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {{
  background: var(--panel) !important;
  border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] * {{
  color: var(--text) !important;
}}

/* ===== DataFrames ===== */
[data-testid="stDataFrame"] {{
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  background: var(--panel);
}}

/* =========================================================
   DROPDOWNS (Select + Multiselect) — HARD FIX
   Closed control follows theme, opened menu is WHITE with BLACK text.
   ========================================================= */

/* Closed control surface */
div[data-baseweb="select"] > div {{
  background-color: var(--control_bg) !important;
  color: var(--control_text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}}
div[data-baseweb="select"] input {{
  color: var(--control_text) !important;
}}
div[data-baseweb="select"] span {{
  color: var(--control_text) !important;
}}
div[data-baseweb="select"] svg {{
  color: var(--control_text) !important;
  fill: var(--control_text) !important;
}}

/* Opened dropdown popover + menu container */
div[data-baseweb="popover"],
div[data-baseweb="menu"] {{
  background: var(--menu_bg) !important;
  color: var(--menu_text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow) !important;
}}

/* The listbox itself */
div[role="listbox"],
ul[role="listbox"] {{
  background: var(--menu_bg) !important;
  color: var(--menu_text) !important;
}}

/* Each option row */
div[role="option"],
li[role="option"] {{
  background: transparent !important;
  color: var(--menu_text) !important;
  padding: 10px 12px !important;
}}
div[role="option"] *,
li[role="option"] * {{
  color: var(--menu_text) !important;
}}

/* Hover / Selected */
div[role="option"]:hover,
li[role="option"]:hover {{
  background: rgba(59,130,246,0.14) !important;
}}
div[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {{
  background: rgba(34,197,94,0.16) !important;
}}

/* =========================================================
   INLINE CODE + CODE BLOCKS
   Fixes: fact_orders_enriched.csv + your st.code(...) list.
   ========================================================= */

/* Inline code (markdown `...`) */
.stMarkdown code, p code, li code, span code {{
  background: var(--code_bg) !important;
  color: var(--code_text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 2px 8px !important;
}}

/* st.code / code blocks */
div[data-testid="stCodeBlock"] {{
  background: var(--code_bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
}}
div[data-testid="stCodeBlock"] pre,
div[data-testid="stCodeBlock"] pre code {{
  background: var(--code_bg) !important;
  color: var(--code_text) !important;
}}

/* Alerts readability */
div[data-testid="stAlert"] {{
  border-radius: 14px !important;
}}
div[data-testid="stAlert"] * {{
  color: var(--text) !important;
}}

</style>
""",
    unsafe_allow_html=True,
)




# =========================
# Paths
# =========================
BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
ANALYTICS_DIR = DATA_DIR / "analytics"

FACT_RAW = ANALYTICS_DIR / "fact_orders.csv"
FACT_ENRICHED = ANALYTICS_DIR / "fact_orders_enriched.csv"
FACT = FACT_ENRICHED if FACT_ENRICHED.exists() else FACT_RAW

# Optional v2 analytics tables (if you generated them)
RISK_SHIPMENTS = ANALYTICS_DIR / "risk_shipments.csv"
EXCEPTIONS = ANALYTICS_DIR / "exceptions.csv"
SEASONALITY = ANALYTICS_DIR / "seasonality_monthly.csv"
SCENARIOS = ANALYTICS_DIR / "scenarios.csv"


# =========================
# Helpers
# =========================
def fmt_compact(n) -> str:
    try:
        n = float(n)
        if abs(n) >= 1_000_000_000:
            return f"{n/1_000_000_000:.1f}B"
        if abs(n) >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if abs(n) >= 1_000:
            return f"{n/1_000:.1f}k"
        return f"{n:,.0f}"
    except Exception:
        return "—"


def fmt_money(n) -> str:
    try:
        return f"{float(n):,.2f}"
    except Exception:
        return "—"


def fmt_pct(x) -> str:
    try:
        return f"{float(x):.1%}"
    except Exception:
        return "—"


def to_date_range(df: pd.DataFrame) -> str:
    if df.empty or "order_date" not in df.columns:
        return "—"
    return f"{df['order_date'].min().date()} to {df['order_date'].max().date()}"


def col_if_exists(df: pd.DataFrame, preferred: str, fallback: str) -> str:
    return preferred if preferred in df.columns else fallback


def pill(label: str, status: str) -> str:
    css = {"ok": "pill-ok", "warn": "pill-warn", "bad": "pill-bad"}.get(status, "pill-warn")
    return f'<span class="pill {css}">{label}</span>'


def kpi_card(title: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
<div class="dashboard-card">
  <div class="card-title">{title}</div>
  <div class="card-value">{value}</div>
  <div class="card-sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_fact(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    for bcol in ["is_on_time", "is_late", "is_early"]:
        if bcol in df.columns and df[bcol].dtype == object:
            df[bcol] = df[bcol].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


@st.cache_data(show_spinner=False)
def load_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=parse_dates) if parse_dates else pd.read_csv(path)


def require_fact() -> None:
    if not FACT.exists():
        st.error(
            "Missing analytics files.\n\n"
            "Run these in order:\n"
            "1) python scripts/02_prepare_data.py\n"
            "2) python scripts/02b_generate_context_mappings.py\n"
            "3) python scripts/02c_apply_context_mappings.py\n\n"
            "Then refresh this page."
        )
        st.stop()


def tight_layout(fig, height: int = 280):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return fig


# =========================
# Header
# =========================
st.title("Supply Chain Control Tower")

# IMPORTANT: single-day dataset => call it what it is
st.caption("Daily Ops Snapshot (single-day dataset): exceptions, hotspots, and cost exposure by lane/carrier.")

require_fact()
fact = load_fact(FACT)

# Single-day detector
is_single_day = False
if "order_date" in fact.columns and len(fact):
    is_single_day = fact["order_date"].dt.date.nunique() == 1

# =========================
# Definitions
# =========================
with st.expander("Definitions, assumptions, and limitations", expanded=False):
    st.markdown(
        """
**Portfolio context:** consumer electronics distributor with global sourcing and EU/UK distribution using multi-modal freight.

**Definitions**
- **Lane:** origin → destination
- **On-time:** `is_on_time == True`
- **Late:** `is_late == True` (or `ship_late_day_count > 0` where present)
- **Risk score (proxy):** prioritisation metric based on cost exposure × service failure

**Dataset limitation**
- This dataset contains a single day of orders, so time-series trends are not shown. The dashboard focuses on daily execution: exceptions, hotspots, and triage.

**Mapping layer (readability for interviews)**
The public dataset uses coded identifiers. To make the dashboard readable, the pipeline can generate
`fact_orders_enriched.csv` with readable fields:
`carrier_name`, `service_tier`, `origin_port_name`, `dest_port_name`, `plant_name`, `product_family`, `customer_segment`, `lane_name`.
The app automatically uses these fields if the enriched file exists.
"""
    )

# =========================
# Tabs
# =========================
tab_exec, tab_risk, tab_trends, tab_data = st.tabs(
    ["Executive Summary", "Risk & Exceptions", "Trends", "Data"]
)

# =========================
# Sidebar filters (plain English when enriched)
# =========================
st.sidebar.header("Filters")

min_date = fact["order_date"].min().date()
max_date = fact["order_date"].max().date()

# If single-day, do not pretend it’s a range
if is_single_day:
    st.sidebar.caption(f"Dataset date: {min_date}")
    start, end = min_date, max_date
else:
    date_range = st.sidebar.date_input("Order date range", (min_date, max_date))
    start, end = (date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date))

f = fact[(fact["order_date"].dt.date >= start) & (fact["order_date"].dt.date <= end)].copy()

carrier_col = col_if_exists(f, "carrier_name", "carrier")
service_col = col_if_exists(f, "service_tier", "svc_cd")
plant_col = col_if_exists(f, "plant_name", "plant_code")
mode_col = "mode_dsc" if "mode_dsc" in f.columns else None
cust_col = col_if_exists(f, "customer_segment", "customer")
prod_col = col_if_exists(f, "product_family", "product_id")

carrier_sel = st.sidebar.multiselect("Carrier", sorted(f[carrier_col].dropna().unique().tolist()))
if carrier_sel:
    f = f[f[carrier_col].isin(carrier_sel)]

service_sel = st.sidebar.multiselect("Service", sorted(f[service_col].dropna().unique().tolist()))
if service_sel:
    f = f[f[service_col].isin(service_sel)]

if mode_col:
    mode_sel = st.sidebar.multiselect("Mode", sorted(f[mode_col].dropna().unique().tolist()))
    if mode_sel:
        f = f[f[mode_col].isin(mode_sel)]

plant_sel = st.sidebar.multiselect("Plant", sorted(f[plant_col].dropna().unique().tolist()))
if plant_sel:
    f = f[f[plant_col].isin(plant_sel)]

st.sidebar.divider()
st.sidebar.caption("Tip: filter to a carrier/service and the risk drivers + exception queue will update.")

# =========================
# Targets
# =========================
TARGET_ON_TIME = 0.98
TARGET_LATE_RATE = 0.02

# =========================
# EXEC SUMMARY
# =========================
with tab_exec:
    st.subheader("Executive summary (scan-and-decide)")

    orders = int(f["order_id"].nunique()) if "order_id" in f.columns else len(f)
    units = float(f.get("unit_quantity", pd.Series([0] * len(f))).fillna(0).sum())
    late_orders = int(f.get("is_late", pd.Series([False] * len(f))).fillna(False).sum())
    on_time_rate = float(f.get("is_on_time", pd.Series([False] * len(f))).fillna(False).mean()) if len(f) else 0.0
    freight_cost = float(f.get("freight_cost_est", pd.Series([0] * len(f))).fillna(0).sum())
    late_rate = (late_orders / orders) if orders else 0.0
    cost_per_order = (freight_cost / orders) if orders else 0.0

    base_orders = int(fact["order_id"].nunique()) if "order_id" in fact.columns else len(fact)
    base_cost = float(fact.get("freight_cost_est", pd.Series([0] * len(fact))).fillna(0).sum())
    base_cost_per_order = (base_cost / base_orders) if base_orders else 0.0

    # KPI tiles
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi_card("Orders", fmt_compact(orders), "Total orders in view")
    with c2: kpi_card("Units", fmt_compact(units), "Total units shipped")
    with c3: kpi_card("Late orders", fmt_compact(late_orders), f"Late rate: {fmt_pct(late_rate)}")
    with c4: kpi_card("On-time rate", fmt_pct(on_time_rate), f"Target: {TARGET_ON_TIME:.0%}")
    with c5: kpi_card("Freight cost", fmt_compact(freight_cost), "Estimated total")
    with c6: kpi_card("Cost / order", fmt_money(cost_per_order), "Vs baseline")

    st.caption(f"Data range in view: {to_date_range(f)}")

    # Status pills
    on_time_status = "ok" if on_time_rate >= TARGET_ON_TIME else ("warn" if on_time_rate >= TARGET_ON_TIME - 0.01 else "bad")
    late_status = "ok" if late_rate <= TARGET_LATE_RATE else ("warn" if late_rate <= TARGET_LATE_RATE + 0.01 else "bad")
    cost_status = "ok" if base_cost_per_order == 0 or cost_per_order <= base_cost_per_order * 1.10 else ("warn" if cost_per_order <= base_cost_per_order * 1.25 else "bad")

    st.markdown(
        pill(f"On-time ≥ {TARGET_ON_TIME:.0%}", on_time_status)
        + pill(f"Late rate ≤ {TARGET_LATE_RATE:.0%}", late_status)
        + pill("Cost/order vs baseline", cost_status),
        unsafe_allow_html=True,
    )

    # =========================
    # ALERT STRIP (cockpit feel)
    # =========================
    st.divider()
    st.subheader("Alerts (where to act first)")

    # Carrier performance
    carrier_stats = (
        f.groupby(carrier_col)
        .agg(
            orders=("order_id", "nunique"),
            on_time_rate=("is_on_time", "mean"),
            late_orders=("is_late", "sum"),
            freight_cost=("freight_cost_est", "sum"),
        )
        .reset_index()
    )

    worst_carrier_name = "—"
    worst_carrier_sub = "No data"
    if not carrier_stats.empty:
        worst = carrier_stats.sort_values(["on_time_rate", "orders"], ascending=[True, False]).head(1)
        worst_carrier_name = str(worst.iloc[0][carrier_col])
        worst_carrier_sub = f"On-time: {fmt_pct(float(worst.iloc[0]['on_time_rate']))} | Orders: {int(worst.iloc[0]['orders'])}"

    # Lane risk = cost × (1 - on_time)
    if "lane_name" in f.columns:
        lane_stats = (
            f.groupby("lane_name")
            .agg(
                orders=("order_id", "nunique"),
                freight_cost=("freight_cost_est", "sum"),
                on_time_rate=("is_on_time", "mean"),
            )
            .reset_index()
            .rename(columns={"lane_name": "lane"})
        )
    else:
        lane_stats = (
            f.groupby(["orig_port_cd", "dest_port_cd"])
            .agg(
                orders=("order_id", "nunique"),
                freight_cost=("freight_cost_est", "sum"),
                on_time_rate=("is_on_time", "mean"),
            )
            .reset_index()
        )
        lane_stats["lane"] = lane_stats["orig_port_cd"].astype(str) + " → " + lane_stats["dest_port_cd"].astype(str)

    lane_stats["risk_score"] = lane_stats["freight_cost"] * (1 - lane_stats["on_time_rate"])
    top_lane = lane_stats.sort_values("risk_score", ascending=False).head(1)

    top_lane_name = "—"
    top_lane_sub = "No data"
    if len(top_lane):
        top_lane_name = str(top_lane.iloc[0]["lane"])
        top_lane_sub = f"Risk: {fmt_compact(float(top_lane.iloc[0]['risk_score']))} | On-time: {fmt_pct(float(top_lane.iloc[0]['on_time_rate']))}"

    late_queue = int(f.get("is_late", pd.Series([False] * len(f))).fillna(False).sum())
    late_cost = float(f.loc[f.get("is_late", False), "freight_cost_est"].fillna(0).sum()) if "freight_cost_est" in f.columns else 0.0

    avg_tpt = "—"
    if "tpt" in f.columns and len(f):
        avg_tpt = f"{float(f['tpt'].mean()):.1f} days"

    a1, a2, a3, a4, a5 = st.columns(5)
    with a1: kpi_card("Worst carrier", worst_carrier_name, worst_carrier_sub)
    with a2: kpi_card("Highest-risk lane", top_lane_name, top_lane_sub)
    with a3: kpi_card("Late queue", fmt_compact(late_queue), "Orders needing action")
    with a4: kpi_card("Late cost exposure", fmt_compact(late_cost), "Estimated freight cost on late orders")
    with a5: kpi_card("Transit time", avg_tpt, "Average TPT (proxy)")

    st.markdown("**What to do:** 1) Stabilise worst carrier, 2) attack top-risk lane, 3) clear high exposure late orders first.")
    st.divider()

        # =========================
    # Driver charts (enterprise cards)
    # =========================
    st.markdown(
        """
<div class="section-card">
  <div class="section-title">Performance drivers</div>
</div>
""",
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3)

    def chart_header(title: str):
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

    # 1) Worst carriers
    with d1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_header("Worst carriers (service reliability)")

        if len(f):
            carrier_stats = (
                f.groupby(carrier_col)
                .agg(
                    orders=("order_id", "nunique"),
                    on_time_rate=("is_on_time", "mean"),
                    late_rate=("is_late", "mean"),
                    freight_cost=("freight_cost_est", "sum"),
                )
                .reset_index()
            )
            carrier_stats = carrier_stats[carrier_stats["orders"] >= 50].copy()

            if carrier_stats.empty:
                st.info("Not enough volume under current filters to rank carriers.")
            else:
                worst = carrier_stats.sort_values(["on_time_rate", "orders"], ascending=[True, False]).head(10).copy()
                worst["segment"] = ["Bottom 3" if i < 3 else "Other" for i in range(len(worst))]

                fig = px.bar(
                    worst,
                    x="on_time_rate",
                    y=carrier_col,
                    orientation="h",
                    color="segment",
                    color_discrete_map={
                        "Bottom 3": css_vars["--bad"],
                        "Other": "rgba(100,116,139,0.85)",
                    },
                    text=worst["on_time_rate"].map(lambda v: f"{v:.0%}"),
                )
                fig.update_layout(
                    template=PLOTLY_TEMPLATE,
                    height=340,
                    xaxis_title=None,
                    yaxis_title=None,
                    legend_title_text=None,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                fig.update_traces(textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickformat=".0%", showgrid=False, zeroline=False)
                fig.update_yaxes(showgrid=False)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Bottom 3 carriers highlighted.")
        else:
            st.info("No data under current filters.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 2) Highest-risk lanes
    with d2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_header("Highest-risk lanes (cost exposure × failure)")

        if len(f):
            if "lane_name" in f.columns:
                lane = (
                    f.groupby("lane_name")
                    .agg(
                        orders=("order_id", "nunique"),
                        freight_cost=("freight_cost_est", "sum"),
                        on_time_rate=("is_on_time", "mean"),
                    )
                    .reset_index()
                    .rename(columns={"lane_name": "lane"})
                )
            else:
                lane = (
                    f.groupby(["orig_port_cd", "dest_port_cd"])
                    .agg(
                        orders=("order_id", "nunique"),
                        freight_cost=("freight_cost_est", "sum"),
                        on_time_rate=("is_on_time", "mean"),
                    )
                    .reset_index()
                )
                lane["lane"] = lane["orig_port_cd"].astype(str) + " → " + lane["dest_port_cd"].astype(str)

            lane = lane[lane["orders"] >= 20].copy()

            if lane.empty:
                st.info("Not enough lane volume under current filters.")
            else:
                lane["risk_score"] = lane["freight_cost"] * (1 - lane["on_time_rate"])
                top = lane.sort_values("risk_score", ascending=False).head(10).copy()

                fig = px.bar(
                    top,
                    x="risk_score",
                    y="lane",
                    orientation="h",
                    color="risk_score",
                    color_continuous_scale=[
                        "rgba(245,158,11,0.20)",
                        "rgba(245,158,11,0.75)",
                        "rgba(239,68,68,0.92)",
                    ],
                    text=top["risk_score"].map(lambda v: f"{v:,.0f}"),
                )
                fig.update_layout(
                    template=PLOTLY_TEMPLATE,
                    height=340,
                    xaxis_title=None,
                    yaxis_title=None,
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                fig.update_traces(textposition="outside", cliponaxis=False)
                fig.update_xaxes(showgrid=False, zeroline=False)
                fig.update_yaxes(showgrid=False)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Amber→red indicates the most critical lanes.")
        else:
            st.info("No data under current filters.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 3) Cost concentration
    with d3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_header("Cost concentration (top spend lanes)")

        if len(f):
            if "lane_name" in f.columns:
                lane_cost = (
                    f.groupby("lane_name")
                    .agg(freight_cost=("freight_cost_est", "sum"))
                    .reset_index()
                    .rename(columns={"lane_name": "lane"})
                )
            else:
                lane_cost = (
                    f.groupby(["orig_port_cd", "dest_port_cd"])
                    .agg(freight_cost=("freight_cost_est", "sum"))
                    .reset_index()
                )
                lane_cost["lane"] = lane_cost["orig_port_cd"].astype(str) + " → " + lane_cost["dest_port_cd"].astype(str)

            topc = lane_cost.sort_values("freight_cost", ascending=False).head(10).copy()

            fig = px.bar(
                topc,
                x="freight_cost",
                y="lane",
                orientation="h",
                color="freight_cost",
                color_continuous_scale=[
                    "rgba(96,165,250,0.25)",
                    "rgba(37,99,235,0.70)",
                    "rgba(30,58,138,0.92)",
                ],
                text=topc["freight_cost"].map(lambda v: f"{v:,.0f}"),
            )
            fig.update_layout(
                template=PLOTLY_TEMPLATE,
                height=340,
                xaxis_title=None,
                yaxis_title=None,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Shows where spend is concentrated by lane.")
        else:
            st.info("No data under current filters.")

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # Exception triage (action queue)
    # =========================
    st.markdown(
        """
<div class="section-card">
  <div class="section-title">Action queue (exception triage)</div>
</div>
""",
        unsafe_allow_html=True,
    )

    late_mask = f.get("is_late", pd.Series([False] * len(f))).fillna(False)
    late_df = f[late_mask].copy()

    if late_df.empty:
        st.info("No late shipments under current filters.")
    else:
        late_df["days_late"] = late_df.get("ship_late_day_count", pd.Series([0] * len(late_df))).fillna(0).astype(float)
        late_df["cost"] = late_df.get("freight_cost_est", pd.Series([0] * len(late_df))).fillna(0).astype(float)
        late_df["priority_score"] = (late_df["days_late"].clip(lower=0) * (late_df["cost"].clip(lower=0) + 1)).astype(float)

        q1 = late_df["priority_score"].quantile(0.70)
        q2 = late_df["priority_score"].quantile(0.90)

        def band(x: float) -> str:
            if x >= q2:
                return "High"
            if x >= q1:
                return "Medium"
            return "Low"

        late_df["priority_band"] = late_df["priority_score"].map(band)

        action_cols = [
            "priority_band",
            "order_id",
            "order_date",
            cust_col if cust_col in late_df.columns else "customer",
            prod_col if prod_col in late_df.columns else "product_id",
            plant_col if plant_col in late_df.columns else "plant_code",
            "origin_port_name" if "origin_port_name" in late_df.columns else "orig_port_cd",
            "dest_port_name" if "dest_port_name" in late_df.columns else "dest_port_cd",
            carrier_col if carrier_col in late_df.columns else "carrier",
            service_col if service_col in late_df.columns else "svc_cd",
            "mode_dsc" if "mode_dsc" in late_df.columns else None,
            "days_late",
            "tpt" if "tpt" in late_df.columns else None,
            "weight" if "weight" in late_df.columns else None,
            "cost",
            "priority_score",
        ]
        action_cols = [c for c in action_cols if c and c in late_df.columns]

        band_order = {"High": 0, "Medium": 1, "Low": 2}
        triage = late_df.copy()
        triage["_band_order"] = triage["priority_band"].map(band_order).fillna(9)
        triage = triage.sort_values(["_band_order", "priority_score"], ascending=[True, False]).head(100).drop(columns=["_band_order"])

        t1, t2, t3, t4 = st.columns(4)
        with t1: kpi_card("Late shipments", fmt_compact(len(late_df)), "Exception queue size")
        with t2: kpi_card("High priority", fmt_compact(int((late_df["priority_band"] == "High").sum())), "Immediate attention")
        with t3: kpi_card("Avg days late", f"{late_df['days_late'].mean():.1f}", "Delay severity")
        with t4: kpi_card("Cost exposure", fmt_compact(late_df["cost"].sum()), "Sum of est. freight cost")

        st.caption("Sorted by priority score (delay × cost exposure). Use filters to narrow focus.")
        st.dataframe(triage[action_cols], use_container_width=True, height=520)



with tab_risk:
    st.subheader("Risk & exceptions (operational radar)")

    # -------------------------
    # Risk shipments (if pipeline output exists)
    # -------------------------
    if RISK_SHIPMENTS.exists():
        risk = load_csv(RISK_SHIPMENTS, parse_dates=["order_date"])
        risk = risk[(risk["order_date"].dt.date >= start) & (risk["order_date"].dt.date <= end)].copy()

        # Align filters (if enriched)
        if "carrier_name" in risk.columns and carrier_sel:
            risk = risk[risk["carrier_name"].isin(carrier_sel)]
        elif "carrier" in risk.columns and carrier_sel:
            risk = risk[risk["carrier"].isin(carrier_sel)]

        st.markdown(
            """
<div class="section-card">
  <div class="section-title">Risk radar</div>
</div>
""",
            unsafe_allow_html=True,
        )

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            kpi_card("Shipments (risk table)", fmt_compact(len(risk)), "Rows in risk output")
        with r2:
            kpi_card(
                "Avg risk score",
                f"{risk['risk_score'].mean():.1f}" if len(risk) and "risk_score" in risk.columns else "—",
                "Prioritisation proxy",
            )
        with r3:
            kpi_card(
                "High risk",
                fmt_compact(int((risk.get("risk_band") == "High").sum())) if "risk_band" in risk.columns else "—",
                "Banding if available",
            )
        with r4:
            kpi_card(
                "Late (risk table)",
                fmt_compact(int(risk.get("is_late", pd.Series([False] * len(risk))).fillna(False).sum())) if len(risk) else "0",
                "Late in risk output",
            )

        # Risk distribution chart
        if "risk_score" in risk.columns and len(risk):
            st.markdown(
                """
<div class="section-card">
  <div class="section-title">Risk score distribution</div>
</div>
""",
                unsafe_allow_html=True,
            )
            fig = px.histogram(risk, x="risk_score", nbins=28)
            fig.update_layout(
                template=PLOTLY_TEMPLATE,
                height=320,
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)

        # Top risk queue (triage list)
        st.markdown(
            """
<div class="section-card">
  <div class="section-title">Top risk queue (triage list)</div>
</div>
""",
            unsafe_allow_html=True,
        )

        show_cols = [c for c in [
            "order_id", "order_date",
            "lane_name" if "lane_name" in risk.columns else ("lane" if "lane" in risk.columns else None),
            "carrier_name" if "carrier_name" in risk.columns else ("carrier" if "carrier" in risk.columns else None),
            "service_tier" if "service_tier" in risk.columns else ("svc_cd" if "svc_cd" in risk.columns else None),
            "mode_dsc" if "mode_dsc" in risk.columns else None,
            "risk_band" if "risk_band" in risk.columns else None,
            "risk_score" if "risk_score" in risk.columns else None,
            "ship_late_day_count" if "ship_late_day_count" in risk.columns else None,
            "freight_cost_est" if "freight_cost_est" in risk.columns else None,
        ] if c]
        show_cols = [c for c in show_cols if c in risk.columns]

        if show_cols and "risk_score" in risk.columns:
            st.dataframe(
                risk.sort_values("risk_score", ascending=False).head(100)[show_cols],
                use_container_width=True,
                height=520,
            )
        else:
            st.dataframe(risk.head(100), use_container_width=True, height=520)

    else:
        st.info("No risk table found (`risk_shipments.csv`). Run: `python scripts/03_build_control_tower_v2.py`")

    st.divider()

    # -------------------------
    # Exceptions queue (if pipeline output exists)
    # -------------------------
    if EXCEPTIONS.exists():
        st.markdown(
            """
<div class="section-card">
  <div class="section-title">Exceptions queue (pipeline output)</div>
</div>
""",
            unsafe_allow_html=True,
        )
        ex_raw = load_csv(EXCEPTIONS)
        parse = ["order_date"] if "order_date" in ex_raw.columns else None
        ex = load_csv(EXCEPTIONS, parse_dates=parse)

        st.dataframe(ex.head(300), use_container_width=True, height=520)
        st.caption("This table is generated by the pipeline for ops triage and root-cause workflows.")
    else:
        st.caption("No `exceptions.csv` found (optional output).")


# =========================
# TRENDS
# =========================
with tab_trends:
    st.subheader("Trends")

    if is_single_day:
        st.info(
            "This project dataset contains a single day of orders, so time-series trends are not available.\n\n"
            "If you want trends, swap to a multi-week/month dataset and keep the same control tower structure."
        )
    else:
        if SEASONALITY.exists():
            s = load_csv(SEASONALITY)
            st.markdown("**Monthly service performance**")

            y_cols = [c for c in ["on_time_rate", "late_rate"] if c in s.columns]
            if "month" in s.columns and y_cols:
                fig = px.line(s, x="month", y=y_cols)
                fig.update_layout(template=PLOTLY_TEMPLATE)
                tight_layout(fig, height=320)
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(s, use_container_width=True, height=380)
        else:
            st.info("No seasonality_monthly.csv found. (Optional)")

        st.divider()

        if SCENARIOS.exists():
            sc = load_csv(SCENARIOS)
            st.markdown("**What-if scenarios**")
            st.dataframe(sc, use_container_width=True, height=320)
        else:
            st.caption("No scenarios.csv found. (Optional)")

# =========================
# DATA (debug + transparency)
# =========================
with tab_data:
    st.subheader("Data transparency (what the dashboard is reading)")

    st.markdown(
        f"""
**Fact table in use:** `{FACT.name}`  
**Rows:** {len(fact):,}  
**Columns:** {len(fact.columns):,}  
**Date range:** {to_date_range(fact)}  
"""
    )

    readable_cols = [c for c in [
        "carrier_name", "service_tier", "origin_port_name", "dest_port_name",
        "plant_name", "product_family", "customer_segment", "lane_name"
    ] if c in fact.columns]

    if readable_cols:
        st.success("Context mapping is ACTIVE (plain-English labels available).")
        st.code(", ".join(readable_cols))
    else:
        st.warning(
            "Context mapping is NOT active yet — you are viewing coded identifiers.\n\n"
            "To enable plain-English labels run:\n"
            "1) python scripts/02b_generate_context_mappings.py\n"
            "2) python scripts/02c_apply_context_mappings.py\n"
        )

    st.divider()
    st.markdown("**Preview**")
    st.dataframe(fact.head(25), use_container_width=True, height=520)
