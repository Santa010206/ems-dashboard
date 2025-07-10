import pandas as pd
from typing import Tuple, Optional
from utils import remove_water_columns

def read_and_process_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:

    try:
        name = uploaded_file.name.lower()

        # Read based on file extension
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="\t")
        else:
            return None, "❌ Unsupported file format. Use .csv, .xlsx, .json, or .txt"

        # Check and convert Date column
        if "Date" not in df.columns:
            return None, "❌ Missing 'Date' column"

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.dropna(subset=["Date"], inplace=True)

        # Drop water-related columns
        df = remove_water_columns(df)

        # Drop unwanted columns
        drop_cols = ["S. No.", "Cwk"]
        df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore", inplace=True)

        # Sort by date
        df_sorted = df.sort_values("Date").reset_index(drop=True)

        # Identify numeric device columns
        ignore_cols = ["Date", "Day"]
        device_cols = [col for col in df_sorted.columns if col not in ignore_cols]

        # Initialize output DataFrame
        consumption_df = df_sorted[["Date"]].copy()

        for col in device_cols:
            df_sorted[col] = pd.to_numeric(df_sorted[col], errors="coerce")
            # Difference between consecutive days
            consumption_df[col] = df_sorted[col].diff()

        # Convert to long format
        long_df = consumption_df.melt(
            id_vars=["Date"],
            value_vars=device_cols,
            var_name="Device",
            value_name="Consumption_kwh"
        )

        # Rename and clean
        long_df.rename(columns={"Date": "Timestamp"}, inplace=True)

        # Drop only NaN (keep 0.0 values)
        long_df.dropna(subset=["Consumption_kwh"], inplace=True)

        # Replace negative values with 0 (if meters roll back or error)
        long_df["Consumption_kwh"] = long_df["Consumption_kwh"].apply(lambda x: max(x, 0))

        return long_df, None

    except Exception as e:
        return None, f"❌ Error processing file: {str(e)}"
