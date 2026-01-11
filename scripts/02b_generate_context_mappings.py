from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = ROOT / "data" / "analytics"
FACT = ANALYTICS / "fact_orders.csv"
CTX = ROOT / "data" / "context"
CTX.mkdir(parents=True, exist_ok=True)

# Deterministic name pools (assigned in sorted-code order)
CARRIER_NAMES = [
    "DHL Global Forwarding", "Kuehne+Nagel", "DB Schenker", "DSV", "Expeditors",
    "CEVA Logistics", "UPS Supply Chain", "FedEx Logistics", "Maersk Logistics",
    "C.H. Robinson", "XPO Logistics", "GEODIS", "Bolloré Logistics", "Panalpina",
]
SERVICE_TIERS = [
    "Air Express", "Air Economy", "Sea FCL", "Sea LCL", "Road Standard",
    "Road Express", "Intermodal", "Courier Priority",
]
PORT_NAMES = [
    "Port of Shanghai", "Port of Shenzhen", "Port of Ningbo-Zhoushan", "Port of Hong Kong",
    "Port of Ho Chi Minh City", "Port of Singapore", "Port of Busan", "Port of Kaohsiung",
    "Port of Rotterdam", "Port of Hamburg", "Port of Antwerp", "Port of Felixstowe",
    "Port of London Gateway", "Port of Southampton", "Port of Bremerhaven",
]
PLANT_NAMES = [
    "Shenzhen Manufacturing Hub", "Shanghai Assembly Plant", "Ningbo Components Plant",
    "Ho Chi Minh Production Site", "Taipei Final Assembly", "Guangzhou Packaging Center",
    "Suzhou Electronics Plant", "Chengdu Sub-Assembly Plant",
]
PRODUCT_FAMILIES = [
    "Laptops", "Smartphones", "Tablets", "Accessories", "Networking Equipment",
    "Wearables", "Audio Devices", "Gaming Peripherals",
]
CUSTOMER_SEGMENTS = [
    "UK Retailer", "EU Retailer", "E-commerce Partner", "Enterprise Reseller",
    "Distributor", "Channel Partner", "Direct Customer",
]

def _assign_names(codes: list[str], names: list[str], fallback_prefix: str) -> pd.DataFrame:
    codes_sorted = sorted(set([str(c) for c in codes if pd.notna(c)]))
    rows = []
    for i, code in enumerate(codes_sorted):
        label = names[i] if i < len(names) else f"{fallback_prefix} {i+1:02d}"
        rows.append((code, label))
    return pd.DataFrame(rows, columns=["code", "name"])

def main() -> None:
    if not FACT.exists():
        raise FileNotFoundError(f"Missing {FACT}. Ensure you have data/analytics/fact_orders.csv")

    df = pd.read_csv(FACT)

    carriers = df["carrier"].dropna().astype(str).unique().tolist() if "carrier" in df.columns else []
    services = df["svc_cd"].dropna().astype(str).unique().tolist() if "svc_cd" in df.columns else []
    orig_ports = df["orig_port_cd"].dropna().astype(str).unique().tolist() if "orig_port_cd" in df.columns else []
    dest_ports = df["dest_port_cd"].dropna().astype(str).unique().tolist() if "dest_port_cd" in df.columns else []
    ports = sorted(set(orig_ports + dest_ports))
    plants = df["plant_code"].dropna().astype(str).unique().tolist() if "plant_code" in df.columns else []
    products = df["product_id"].dropna().astype(str).unique().tolist() if "product_id" in df.columns else []
    customers = df["customer"].dropna().astype(str).unique().tolist() if "customer" in df.columns else []

    carriers_map = _assign_names(carriers, CARRIER_NAMES, "Carrier")
    services_map = _assign_names(services, SERVICE_TIERS, "Service")
    ports_map = _assign_names(ports, PORT_NAMES, "Port")
    plants_map = _assign_names(plants, PLANT_NAMES, "Plant")
    products_map = _assign_names(products, PRODUCT_FAMILIES, "Product")

    cust_sorted = sorted(set([str(c) for c in customers if pd.notna(c)]))
    cust_rows = []
    for i, c in enumerate(cust_sorted):
        seg = CUSTOMER_SEGMENTS[i % len(CUSTOMER_SEGMENTS)] if CUSTOMER_SEGMENTS else "Customer"
        cust_rows.append((c, seg))
    customers_map = pd.DataFrame(cust_rows, columns=["code", "name"])

    (CTX / "carriers.csv").write_text(carriers_map.to_csv(index=False))
    (CTX / "services.csv").write_text(services_map.to_csv(index=False))
    (CTX / "ports.csv").write_text(ports_map.to_csv(index=False))
    (CTX / "plants.csv").write_text(plants_map.to_csv(index=False))
    (CTX / "products.csv").write_text(products_map.to_csv(index=False))
    (CTX / "customers.csv").write_text(customers_map.to_csv(index=False))

    print("Generated context mappings in data/context/")
    print(f"carriers={len(carriers_map)} services={len(services_map)} ports={len(ports_map)} plants={len(plants_map)} products={len(products_map)} customers={len(customers_map)}")

if __name__ == "__main__":
    main()
