from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

EXCEL_FILE = RAW_DIR / "Supply chain logistics problem.xlsx"

def main():
    print("Loading dataset:", EXCEL_FILE)

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found at {EXCEL_FILE}. "
            "Upload the .xlsx into data/raw/ with the exact same filename."
        )

    xls = pd.ExcelFile(EXCEL_FILE)
    print("Sheets found:", xls.sheet_names)

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)

        # basic column cleanup
        df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]

        out_file = PROCESSED_DIR / f"{sheet}.csv"
        df.to_csv(out_file, index=False)

        print(f"Saved {out_file} | Rows: {len(df)} | Cols: {len(df.columns)}")

if __name__ == "__main__":
    main()
