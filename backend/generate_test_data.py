import json
import random
import requests

random.seed(7)

API = "http://127.0.0.1:8001/predict"
COMMODITIES = [
    "Bottle gourd", "Snakeguard", "Ridgeguard(Tori)", "Potato",
    "Cucumbar(Kheera)", "Pumpkin", "Amaranthus", "Cauliflower",
    "Cowpea(Veg)", "Onion Green", "Capsicum", "Tapioca", "Brinjal",
    "Green Peas", "Grapes", "Carrot", "Cotton", "Ashgourd", "Banana",
    "Soanf", "Knool Khol", "Mustard", "Wheat", "Ginger(Green)", "Spinach",
    "Groundnut", "Cabbage", "Green Chilli", "Onion", "Banana - Green",
    "Coconut", "Beetroot", "Rice", "Paddy(Common)", "Mint(Pudina)",
]


def fetch_predictions(days: int = 15) -> dict:
    all_preds = {}
    for c in COMMODITIES:
        r = requests.post(API, json={"commodity": c, "variety": "Other", "days": days}, timeout=15)
        if r.status_code == 200:
            fb = r.json()["forecast_breakdown"]
            all_preds[c] = {x["date"]: max(x["price"], 200) for x in fb}
    return all_preds


def generate_actuals(predictions: dict, noise_pct: float = 0.22) -> dict:
    actuals = {}
    for commodity, date_prices in predictions.items():
        actuals[commodity] = {
            dt: round(price * random.uniform(1 - noise_pct, 1 + noise_pct))
            for dt, price in date_prices.items()
        }
    return actuals


if __name__ == "__main__":
    print("Fetching predictions ...")
    preds = fetch_predictions(days=15)
    print(f"Got predictions for {len(preds)} commodities")

    actuals = generate_actuals(preds)

    with open("data/predictions.json", "w") as f:
        json.dump(preds, f, indent=2)

    with open("data/actuals.json", "w") as f:
        json.dump(actuals, f, indent=2)

    print("Saved: data/predictions.json, data/actuals.json")
