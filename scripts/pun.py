import os
import pandas as pd
import sqlite3

# === Percorsi ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "pun_index_gme.csv")
DB_PATH = os.path.join(BASE_DIR, "db", "data.db")  # singolo DB

# === Carica il CSV ===
try:
    df = pd.read_csv(CSV_PATH, delimiter=";", encoding="utf-8")
    print("✅ CSV loaded.")
except FileNotFoundError:
    print(f"❌ File not found: {CSV_PATH}")
    exit(1)

# === Pulizia colonne ===
df.columns = [col.strip().lower() for col in df.columns]

column_mapping = {
    "data": "date",
    "€/mwh": "price",
    "prezzo": "price",
    "giorno": "date"
}
df.rename(columns=column_mapping, inplace=True)

if "date" not in df.columns or "price" not in df.columns:
    print(f"❌ Columns 'date' and/or 'price' missing. Found: {list(df.columns)}")
    exit(1)

df["price"] = df["price"].astype(str).str.replace(",", ".", regex=False).astype(float)
df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.strftime("%Y-%m-%d")  # Uniforma formato

df = df.sort_values("date")

# === Scrittura nel DB ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pun_prices (
    date TEXT PRIMARY KEY,
    price REAL
)
""")

df[["date", "price"]].to_sql("pun_prices", conn, if_exists="replace", index=False)

print(f"✅ Data written to DB: {DB_PATH} (table: pun_prices)")
preview = pd.read_sql("SELECT * FROM pun_prices LIMIT 5", conn)
print("📊 Preview:")
print(preview)

conn.close()
print("🏁 Done.")
