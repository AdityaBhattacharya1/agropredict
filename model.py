import pandas as pd
from prophet import Prophet
import pickle
import os
import json
import glob


def train_mandi_model(data_folder, commodity_name):
    all_records = []

    file_pattern = os.path.join(data_folder, "commodity_prices-*.json")
    files = glob.glob(file_pattern)

    if not files:
        print("No data files found in the specified folder.")
        return

    for file_path in files:
        with open(file_path, "r") as f:
            data = json.load(f)
            if "records" in data:
                all_records.extend(data["records"])

    df = pd.DataFrame(all_records)

    # Filter and clean
    df = df[df["commodity"] == commodity_name].copy()
    df["ds"] = pd.to_datetime(df["arrival_date"], dayfirst=True)
    df["y"] = pd.to_numeric(df["modal_price"], errors="coerce")
    df = df.dropna(subset=["ds", "y"])

    df = df.groupby("ds")["y"].mean().reset_index()

    if len(df) < 2:
        print(f"Need at least 2 unique days. Found: {len(df)}")
        return

    model = Prophet(
        yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False
    )

    model.fit(df)

    os.makedirs("models", exist_ok=True)
    with open(f"models/{commodity_name.lower()}_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"Model for {commodity_name} trained using {len(df)} days of data.")


if __name__ == "__main__":
    train_mandi_model("data", "Potato")
