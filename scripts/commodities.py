import requests
import sqlite3
import time
import os
from dotenv import load_dotenv

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv()
API_KEY = os.getenv("TRADEFEEDS_API_KEY")

# === CONFIGURATION ===
COMMODITIES = ["crude_oil", "ttf_gas", "gasoline", "brent", "coal"]
YEAR_RANGES = [
    ("2020-01-01", "2020-12-31"),
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31")
]

# === DATABASE SETUP ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "db")
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, "data.db")  # unified DB

# === CONNECT TO DATABASE ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === CREATE TABLE IF NOT EXISTS ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS commodity_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commodity TEXT,
    date TEXT,
    price REAL,
    unit TEXT,
    UNIQUE(commodity, date)
)
""")
conn.commit()

# === FUNCTION: FETCH AND STORE DATA ===
def fetch_and_store_commodity(name, start_date, end_date):
    print(f"📥 Downloading: {name} ({start_date} → {end_date})")
    url = "https://data.tradefeeds.com/api/v1/commodity_historical"
    params = {
        "key": API_KEY,
        "name": name,
        "date_from": start_date,
        "date_to": end_date,
        "frequency": "day"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"❌ Error for {name}: {response.status_code} - {response.text}")
        return

    data = response.json()
    result = data.get("result", {})
    output = result.get("output")

    if isinstance(output, list):
        output = output[0]

    if not output or "prices" not in output:
        print(f"⚠️ No 'prices' field found for {name} ({start_date})")
        return

    prices_raw = output["prices"]
    unit = output.get("unit", "unknown")

    if isinstance(prices_raw, dict):
        prices_raw = [prices_raw]

    count = 0
    for entry in prices_raw:
        date = entry["date"]
        price = float(entry["price"])

        cursor.execute("""
            INSERT OR IGNORE INTO commodity_prices (commodity, date, price, unit)
            VALUES (?, ?, ?, ?)
        """, (name, date, price, unit))
        count += 1

    conn.commit()
    print(f"✅ {name} ({start_date}): {count} records saved.")

# === LOOP THROUGH COMMODITIES AND YEARS ===
for commodity in COMMODITIES:
    for start_date, end_date in YEAR_RANGES:
        fetch_and_store_commodity(commodity, start_date, end_date)
        time.sleep(1)  # prevent API rate limit issues

# === CLOSE CONNECTION ===
conn.close()
print("🏁 Done.")
