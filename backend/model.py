import pandas as pd
from prophet import Prophet
import pickle
import os
import json
import glob
from commodities import commodity_list


def train_mandi_model_pro(data_folder, commodity_name, variety="Other"):
    all_records = []
    file_pattern = os.path.join(data_folder, "commodity_prices-*.json")
    files = glob.glob(file_pattern)

    if not files:
        print("No data files found.")
        return

    for file_path in files:
        with open(file_path, "r") as f:
            data = json.load(f)
            if "records" in data:
                all_records.extend(data["records"])

    df = pd.DataFrame(all_records)

    df = df[(df["commodity"] == commodity_name) & (df["variety"] == variety)].copy()

    # Clean and Convert
    df["ds"] = pd.to_datetime(df["arrival_date"], dayfirst=True)
    for col in ["modal_price", "min_price", "max_price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["ds", "modal_price"])

    # 2. Feature Engineering: Price Spread (Volatility Signal)
    df["spread"] = df["max_price"] - df["min_price"]

    # Aggregate daily
    daily_df = (
        df.groupby("ds").agg({"modal_price": "mean", "spread": "mean"}).reset_index()
    )

    daily_df = daily_df.rename(columns={"modal_price": "y"})

    if len(daily_df) < 3:
        print(f"Insufficient data for advanced modeling ({len(daily_df)} days found).")
        return

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    model.add_country_holidays(country_name="IN")

    model.add_regressor("spread")

    model.fit(daily_df)

    os.makedirs("models", exist_ok=True)
    model_name = f"{commodity_name}_{variety}".lower().replace(" ", "_")
    with open(f"models/{model_name}_model.pkl", "wb") as f:
        pickle.dump(model, f)

    latest_spread = daily_df["spread"].iloc[-1]
    with open(f"models/{model_name}_meta.json", "w") as f:
        json.dump({"latest_spread": float(latest_spread)}, f)

    print(f"Model for {commodity_name} ({variety}) trained!")


if __name__ == "__main__":
    for commodity in commodity_list:
        train_mandi_model_pro("data", commodity, "Other")
