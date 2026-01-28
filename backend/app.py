import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple
import pickle
import json
import os
import glob
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="AgroPredict Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ForecastRequest(BaseModel):
    commodity: str
    variety: str = "Other"
    days: int = 15


def load_resources(commodity: str, variety: str) -> Tuple:
    name = f"{commodity}_{variety}".lower().replace(" ", "_")
    model_path = f"models/{name}_model.pkl"
    meta_path = f"models/{name}_meta.json"

    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        return None, None

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(meta_path, "r") as f:
        meta = json.load(f)

    return model, meta


def generate_smart_advice(df: pd.DataFrame) -> Dict:
    initial_price = df["yhat"].iloc[0]
    final_price = df["yhat"].iloc[-1]
    max_price_row = df.loc[df["yhat"].idxmax()]

    pct_change = ((final_price - initial_price) / initial_price) * 100
    avg_spread = (df["yhat_upper"] - df["yhat_lower"]).mean()
    volatility_index = (avg_spread / df["yhat"].mean()) * 100

    if pct_change > 5:
        recommendation = "Strong Bullish (Hold for Peak)"
        action = "HOLD"
    elif 1 < pct_change <= 5:
        recommendation = "Moderate Uptrend"
        action = "HOLD/ACCUMULATE"
    elif -1 <= pct_change <= 1:
        recommendation = "Stable/Sideways Market"
        action = "NEUTRAL"
    elif -5 < pct_change < -1:
        recommendation = "Moderate Downtrend"
        action = "SELL SOON"
    else:
        recommendation = "Strong Bearish (Price Crash Likely)"
        action = "EXIT IMMEDIATELY"

    return {
        "trend_analysis": recommendation,
        "suggested_action": action,
        "expected_return_pct": round(pct_change, 2),
        "volatility_risk": "High" if volatility_index > 10 else "Low",
        "best_day_to_sell": {
            "date": max_price_row["ds"].strftime("%Y-%m-%d"),
            "estimated_peak_price": round(max_price_row["yhat"], 2),
        },
    }


@app.get("/varieties/{commodity}")
async def get_varieties(commodity: str):
    data_folder = "data"
    file_pattern = os.path.join(data_folder, "commodity_prices-*.json")
    files = glob.glob(file_pattern)

    varieties = set()
    for file_path in files:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if "records" in data:
                    for record in data["records"]:
                        if record.get("commodity", "").lower() == commodity.lower():
                            varieties.add(record.get("variety", "Other"))
        except Exception:
            continue

    if not varieties:
        raise HTTPException(
            status_code=404, detail=f"No varieties found for {commodity}"
        )

    return {"commodity": commodity, "varieties": sorted(list(varieties))}


@app.post("/predict")
async def get_forecast(request: ForecastRequest):
    model, meta = load_resources(request.commodity, request.variety)
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model for {request.commodity} ({request.variety}) not found",
        )

    future = model.make_future_dataframe(periods=request.days)
    future["spread"] = meta["latest_spread"]

    forecast = model.predict(future)
    predictions = forecast.tail(request.days).copy()

    intelligence = generate_smart_advice(predictions)

    daily_data = []
    for _, row in predictions.iterrows():
        daily_data.append(
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "price": round(row["yhat"], 2),
                "range": [round(row["yhat_lower"], 2), round(row["yhat_upper"], 2)],
            }
        )

    return {
        "commodity": request.commodity,
        "variety": request.variety,
        "market_intelligence": intelligence,
        "forecast_breakdown": daily_data,
    }
