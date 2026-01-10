from pathlib import Path
import pandas as pd
import numpy as np

PROCESSED_DIR = Path("data/processed")
ANALYTICS_DIR = Path("data/analytics")
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

def _clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def _to_datetime(df: pd.DataFrame, col: str) -> None:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

def main():
    # ---------- Load ----------
    orders = pd.read_csv(PROCESSED_DIR / "OrderList.csv")
    freight = pd.read_csv(PROCESSED_DIR / "FreightRates.csv")
    wh_caps = pd.read_csv(PROCESSED_DIR / "WhCapacities.csv")
    wh_costs = pd.read_csv(PROCESSED_DIR / "WhCosts.csv")
    plant_ports = pd.read_csv(PROCESSED_DIR / "PlantPorts.csv")
    prod_per_plant = pd.read_csv(PROCESSED_DIR / "ProductsPerPlant.csv")
    vmi = pd.read_csv(PROCESSED_DIR / "VmiCustomers.csv")

    # ---------- Clean column names ----------
    orders = _clean_cols(orders)
    freight = _clean_cols(freight)
    wh_caps = _clean_cols(wh_caps)
    wh_costs = _clean_cols(wh_costs)
    plant_ports = _clean_cols(plant_ports)
    prod_per_plant = _clean_cols(prod_per_plant)
    vmi = _clean_cols(vmi)

    # ---------- Types ----------
    _to_datetime(orders, "order_date")

    # Ensure numeric
    for col in ["unit_quantity", "weight", "tpt", "ship_ahead_day_count", "ship_late_day_count"]:
        if col in orders.columns:
            orders[col] = pd.to_numeric(orders[col], errors="coerce")

    for col in ["minm_wgh_qty", "max_wgh_qty", "minimum_cost", "rate", "tpt_day_cnt"]:
        if col in freight.columns:
            freight[col] = pd.to_numeric(freight[col], errors="coerce")

    # ---------- Performance flags ----------
    orders["is_late"] = (orders.get("ship_late_day_count", 0).fillna(0) > 0)
    orders["is_early"] = (orders.get("ship_ahead_day_count", 0).fillna(0) > 0)
    orders["is_on_time"] = ~orders["is_late"]

    # ---------- Freight cost estimation ----------
    # Match keys:
    # orders.origin_port -> freight.orig_port_cd
    # orders.destination_port -> freight.dest_port_cd
    # orders.carrier -> freight.carrier
    # orders.service_level -> freight.svc_cd
    #
    # and weight must fall in [minm_wgh_qty, max_wgh_qty]
    orders_for_merge = orders.rename(columns={
        "origin_port": "orig_port_cd",
        "destination_port": "dest_port_cd",
        "carrier": "carrier",
        "service_level": "svc_cd"
    })

    # Merge on lane+carrier+service, then filter weight bands
    merged = orders_for_merge.merge(
        freight,
        on=["carrier", "orig_port_cd", "dest_port_cd", "svc_cd"],
        how="left",
        suffixes=("", "_fr")
    )
    # Ensure we have a consistent carrier column name after merges
    # (Sometimes merges create carrier_x / carrier_y depending on upstream columns)
    if "carrier" not in merged.columns:
        for alt in ["carrier_x", "carrier_y", "carrier_fr"]:
            if alt in merged.columns:
                merged = merged.rename(columns={alt: "carrier"})
                break


    # Weight-band filter (keep only rows where weight falls in band)
    w = merged["weight"]
    band_ok = (w >= merged["minm_wgh_qty"]) & (w <= merged["max_wgh_qty"])
    merged["band_ok"] = band_ok

    # For rows with multiple matches, keep the best match:
    # prefer band_ok True; if none, keep first (will produce NaNs).
    merged.sort_values(by=["order_id", "band_ok"], ascending=[True, False], inplace=True)
    merged = merged.drop_duplicates(subset=["order_id"], keep="first")

    # Compute estimated freight cost
    # cost = max(minimum_cost, weight * rate)
    merged["freight_cost_est"] = np.where(
        merged["rate"].notna() & merged["weight"].notna(),
        np.maximum(merged["minimum_cost"].fillna(0), merged["weight"] * merged["rate"]),
        np.nan
    )

    # ---------- Warehouse capacity & cost enrichment ----------
    # WhCapacities: plant_id, daily_capacity
    wh_caps = wh_caps.rename(columns={"plant_id": "plant_code"})
    merged = merged.merge(wh_caps, on="plant_code", how="left")

    # WhCosts: wh, cost/unit (these WH values appear to be PLANTxx in your sample)
    wh_costs = wh_costs.rename(columns={"wh": "plant_code", "cost/unit": "wh_cost_per_unit"})
    merged = merged.merge(wh_costs, on="plant_code", how="left")

    # ---------- Core analytics table ----------
    fact_orders = merged[[
    "order_id", "order_date",
    "orig_port_cd", "dest_port_cd",
    "carrier",  # <-- ADD THIS LINE
    "plant_code", "customer", "product_id",
    "unit_quantity", "weight",
    "tpt", "svc_cd",
    "ship_ahead_day_count", "ship_late_day_count",
    "is_on_time", "is_late", "is_early",
    "mode_dsc", "carrier_type",
    "minimum_cost", "rate", "freight_cost_est",
    "daily_capacity", "wh_cost_per_unit",
]].copy()


    fact_orders.to_csv(ANALYTICS_DIR / "fact_orders.csv", index=False)

    # ---------- Summary KPI tables ----------

    # Daily orders trend
    daily = fact_orders.groupby(pd.to_datetime(fact_orders["order_date"]).dt.date).agg(
        orders=("order_id", "nunique"),
        units=("unit_quantity", "sum"),
        weight=("weight", "sum"),
        freight_cost=("freight_cost_est", "sum"),
        on_time_rate=("is_on_time", "mean"),
        late_orders=("is_late", "sum"),
    ).reset_index().rename(columns={"order_date": "date"})
    daily.to_csv(ANALYTICS_DIR / "kpi_daily.csv", index=False)

    # Lane performance
    lane = fact_orders.groupby(["orig_port_cd", "dest_port_cd"]).agg(
        orders=("order_id", "nunique"),
        units=("unit_quantity", "sum"),
        freight_cost=("freight_cost_est", "sum"),
        on_time_rate=("is_on_time", "mean"),
        avg_tpt=("tpt", "mean"),
    ).reset_index()
    lane.to_csv(ANALYTICS_DIR / "kpi_lane.csv", index=False)

    # Debug print — put it here
    print("fact_orders columns:", fact_orders.columns.tolist())

    # Carrier performance
    carrier = fact_orders.groupby(["carrier", "mode_dsc", "carrier_type"]).agg(
        orders=("order_id", "nunique"),
        freight_cost=("freight_cost_est", "sum"),
        on_time_rate=("is_on_time", "mean"),
        avg_tpt=("tpt", "mean"),
    ).reset_index()
    carrier.to_csv(ANALYTICS_DIR / "kpi_carrier.csv", index=False)


    # Carrier performance
    carrier = fact_orders.groupby(["carrier", "mode_dsc", "carrier_type"]).agg(
        orders=("order_id", "nunique"),
        freight_cost=("freight_cost_est", "sum"),
        on_time_rate=("is_on_time", "mean"),
        avg_tpt=("tpt", "mean"),
    ).reset_index()
    carrier.to_csv(ANALYTICS_DIR / "kpi_carrier.csv", index=False)

    # Plant throughput and capacity utilisation (proxy)
    # Daily capacity is "units/day" but dataset units are not necessarily "units"; treat as proxy
    plant = fact_orders.groupby("plant_code").agg(
        orders=("order_id", "nunique"),
        units=("unit_quantity", "sum"),
        avg_daily_capacity=("daily_capacity", "mean"),
        wh_cost_per_unit=("wh_cost_per_unit", "mean"),
    ).reset_index()
    plant["capacity_util_proxy"] = plant["units"] / (plant["avg_daily_capacity"] * 30)  # monthly proxy
    plant.to_csv(ANALYTICS_DIR / "kpi_plant.csv", index=False)

    print("Saved analytics tables to:", ANALYTICS_DIR)
    print("fact_orders rows:", len(fact_orders))

if __name__ == "__main__":
    main()


