"""
Cleans and standardises the raw dataset into /data/processed for dashboards.
Keeps it simple and repeatable (weekend scope).
"""

from pathlib import Path
import pandas as pd

RAW = Path("data/raw/supply_chain_data_raw.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(RAW)

    # Basic cleanup
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Example: if your dataset has date columns, convert them
    # Update these names once you see actual columns
    for col in ["order_date", "shipping_date", "delivery_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Remove fully empty rows
    df = df.dropna(how="all")

    # Save a single “dashboard-ready” table (weekend scope)
    out = OUT_DIR / "fact_supply_chain.csv"
    df.to_csv(out, index=False)

    print("Saved:", out, "Shape:", df.shape)

if __name__ == "__main__":
    main()

