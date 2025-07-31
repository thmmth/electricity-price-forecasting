import os
import sqlite3
from datetime import datetime
import pandas as pd
from meteostat import Point, Daily

# === CONFIG ===

START = datetime(2020, 1, 1)
END = datetime(2024, 12, 31)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "db")
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, "data.db")  # singolo DB

CITIES = {
    "milano": (45.4642, 9.19),
    "roma": (41.9028, 12.4964),
    "bologna": (44.4949, 11.3426),
    "torino": (45.0703, 7.6869),
    "venezia": (45.4408, 12.3155),
    "napoli": (40.8518, 14.2681),
    "bari": (41.1171, 16.8719),
    "palermo": (38.1157, 13.3615),
    "cagliari": (39.2238, 9.1217)
}

# === CONNESSIONE DB ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_data (
    city TEXT,
    time TEXT,
    tavg REAL,
    tmin REAL,
    tmax REAL,
    prcp REAL,
    snow REAL,
    wdir REAL,
    wspd REAL,
    wpgt REAL,
    pres REAL,
    tsun REAL,
    PRIMARY KEY (city, time)
)
""")
conn.commit()

# === SCARICA E SALVA DATI ===
for city, (lat, lon) in CITIES.items():
    print(f"📥 Fetching weather data for {city.title()}")
    point = Point(lat, lon)
    df = Daily(point, START, END).fetch().reset_index()

    if df.empty:
        print(f"⚠️ No data for {city}")
        continue

    df["time"] = df["time"].dt.strftime("%Y-%m-%d")  # Uniforma formato
    df["city"] = city
    df = df[["city"] + [col for col in df.columns if col != "city"]]  # Ordine colonne

    df.to_sql("weather_data", conn, if_exists="append", index=False)
    print(f"✅ {city}: {len(df)} rows inserted")

conn.close()
print("🏁 Done.")
