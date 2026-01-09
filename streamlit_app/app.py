"""
Streamlit application for the Supply Chain Control Tower Dashboard.

This script serves as the entry point for the Streamlit web app.  It loads processed
data (to be placed in the `data/processed/` directory) and displays key
performance indicators (KPIs) and visualisations.  As the project evolves,
additional pages and interactive elements can be added here.
"""

import streamlit as st
import pandas as pd


def load_data() -> pd.DataFrame:
    """Load processed data for the dashboard.

    Returns an empty DataFrame if no processed file is present.  Replace this
    logic with code that reads your specific processed dataset (e.g. CSV or
    Excel) once you have prepared the data in the `data/processed/` folder.
    """
    try:
        # Example: load a CSV file named 'processed_data.csv' from data/processed
        data_path = "../data/processed/processed_data.csv"
        df = pd.read_csv(data_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def main() -> None:
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Supply Chain Control Tower Dashboard", layout="wide")

    st.title("Supply Chain Control Tower Dashboard")
    st.markdown(
        """
        This interactive dashboard provides insights into key supply chain metrics
        such as on‑time delivery rate, average delivery time and route performance.  Use
        the filters and charts below to explore the data.
        """
    )

    # Load data
    df = load_data()

    if df.empty:
        st.warning(
            "No processed data found. Please place your processed dataset in '
            "data/processed/' and update the `load_data` function accordingly."
        )
        return

    # Display basic statistics
    st.subheader("Data Overview")
    st.write(df.describe(include="all"))

    # Example KPI: On‑Time Delivery Rate
    if "on_time" in df.columns:
        on_time_rate = df["on_time"].mean() * 100
        st.metric("On‑Time Delivery Rate", f"{on_time_rate:.2f}%")

    # Additional charts and filters go here
    # For example:
    # st.bar_chart(...)


if __name__ == "__main__":
    main()