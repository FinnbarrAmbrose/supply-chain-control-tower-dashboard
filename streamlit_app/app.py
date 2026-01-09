import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Supply Chain Control Tower", layout="wide")

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "fact_supply_chain.csv"

st.title("Supply Chain Control Tower Dashboard")

if not DATA_PATH.exists():
    st.warning("Processed dataset not found. Run scripts/01_download_dataset.py then scripts/02_prepare_data.py")
    st.stop()

df = pd.read_csv(DATA_PATH)

st.subheader("Dataset Preview")
st.dataframe(df.head(50), use_container_width=True)

st.subheader("Basic Profile")
col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{df.shape[1]:,}")
col3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
