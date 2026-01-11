from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = ROOT / "data" / "analytics"
CTX = ROOT / "data" / "context"

FACT_IN = ANALYTICS / "fact_orders.csv"
FACT_OUT = ANALYTICS / "fact_orders_enriched.csv"

def _load_map(filename: str, key_col: str, out_col: str) -> pd.DataFrame:
    path = CTX / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run scripts/02b_generate_context_mappings.py first.")
    m = pd.read_csv(path).rename(columns={"code": key_col, "name": out_col})
    m[key_col] = m[key_col].astype(str)
    return m[[key_col, out_col]]

def main() -> None:
    if not FACT_IN.exists():
        raise FileNotFoundError(f"Missing {FACT_IN}. Ensure data/analytics/fact_orders.csv exists.")

    df = pd.read_csv(FACT_IN)

    # normalize join keys
    for col in ["carrier", "svc_cd", "orig_port_cd", "dest_port_cd", "plant_code", "product_id", "customer"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    carriers = _load_map("carriers.csv", "carrier", "carrier_name")
    services = _load_map("services.csv", "svc_cd", "service_tier")
    ports_o = _load_map("ports.csv", "orig_port_cd", "origin_port_name")
    ports_d = _load_map("ports.csv", "dest_port_cd", "dest_port_name")
    plants = _load_map("plants.csv", "plant_code", "plant_name")
    products = _load_map("products.csv", "product_id", "product_family")
    customers = _load_map("customers.csv", "customer", "customer_segment")

    df = df.merge(carriers, on="carrier", how="left")
    df = df.merge(services, on="svc_cd", how="left")
    df = df.merge(ports_o, on="orig_port_cd", how="left")
    df = df.merge(ports_d, on="dest_port_cd", how="left")
    df = df.merge(plants, on="plant_code", how="left")
    df = df.merge(products, on="product_id", how="left")
    df = df.merge(customers, on="customer", how="left")

    # readable lane
    df["lane_name"] = df["origin_port_name"].fillna(df["orig_port_cd"]) + " → " + df["dest_port_name"].fillna(df["dest_port_cd"])

    df.to_csv(FACT_OUT, index=False)
    print(f"Wrote: {FACT_OUT}")
    print("Added columns: carrier_name, service_tier, origin_port_name, dest_port_name, plant_name, product_family, customer_segment, lane_name")

if __name__ == "__main__":
    main()
