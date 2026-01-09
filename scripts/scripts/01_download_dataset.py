"""
Downloads the Kaggle dataset and saves a copy to /data/raw

Dataset: shivaiyer129/supply-chain-data-set
"""

from pathlib import Path
import kagglehub
from kagglehub import KaggleDatasetAdapter

DATASET = "shivaiyer129/supply-chain-data-set"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# IMPORTANT:
# Set this to the exact filename shown in Kaggle > Data tab
FILE_PATH = "supply_chain_data.csv"  # <-- change if Kaggle uses a different name

def main():
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        DATASET,
        FILE_PATH
    )

    out_path = RAW_DIR / "supply_chain_data_raw.csv"
    df.to_csv(out_path, index=False)

    print("Saved:", out_path)
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))

if __name__ == "__main__":
    main()
