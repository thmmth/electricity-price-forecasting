import os
import pandas as pd
import sqlite3

# === PATH SETUP ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "load_forecast.csv")
DB_PATH = os.path.join(BASE_DIR, "db", "data.db")

# === LOAD CSV ===
try:
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8")
    print("✅ CSV loaded successfully.")
except FileNotFoundError:
    print(f"❌ File not found: {CSV_PATH}")
    exit(1)


# === CLEAN COLUMNS ===
df.columns = [col.strip() for col in df.columns]

expected_cols = ["Date", "Zone", "Load [MW]"]
if not all(col in df.columns for col in expected_cols):
    print(f"❌ Missing required columns. Found: {list(df.columns)}")
    exit(1)

# === CONVERT AND CLEAN DATA ===
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
df.dropna(subset=["Date", "Zone", "Load [MW]"], inplace=True)

# === AGGREGATE BY DATE AND ZONE ===
agg_df = df.groupby(["Date", "Zone"], as_index=False)["Load [MW]"].sum()

# === RENAME COLUMNS FOR DATABASE ===
agg_df.rename(columns={
    "Date": "date",
    "Zone": "zone",
    "Load [MW]": "load_mw"
}, inplace=True)

# === WRITE TO DATABASE ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS load_forecast (
    date TEXT,
    zone TEXT,
    load_mw REAL,
    PRIMARY KEY (date, zone)
)
""")

agg_df.to_sql("load_forecast", conn, if_exists="replace", index=False)

print(f"✅ Data written to DB: {DB_PATH} (table: load_forecast)")
preview = pd.read_sql("SELECT * FROM load_forecast LIMIT 5", conn)
print("📊 Preview:")
print(preview)

conn.close()
print("🏁 Done.")


