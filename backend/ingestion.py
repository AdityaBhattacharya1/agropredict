import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def fetch_daily_mandi_data():
    api_key = os.getenv("DATAGOV_API_KEY")
    if not api_key:
        print("Error: DATAGOV_API_KEY not found in environment variables")
        return

    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {"api-key": api_key, "format": "json", "offset": 0, "limit": 10000}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        today_str = datetime.now().strftime("%Y-%m-%d")
        os.makedirs("data", exist_ok=True)
        file_path = f"data/commodity_prices-{today_str}.json"

        with open(file_path, "w") as f:
            json.dump(data, f)

        print(f"Successfully saved: {file_path}")

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    fetch_daily_mandi_data()
