import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import os
import re
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "medease_db"),
    "user": os.getenv("POSTGRES_USER", "medease"),
    "password": os.getenv("POSTGRES_PASSWORD", "medease123"),
}

def clean_html(html_str):
    if pd.isna(html_str) or not html_str:
        return ""
    return re.sub(r'<[^>]+>', ' ', str(html_str)).strip()

df = pd.read_csv("data/generic.csv")
df = df.rename(columns={
    "generic id": "id",
    "generic name": "generic_name",
    "drug class": "drug_class",
    "indication": "indication",
    "indication description": "indication_desc",
    "pharmacology description": "pharmacology",
    "dosage description": "dosage",
    "side effects description": "side_effects",
    "precautions description": "precautions",
})

for col in ["indication_desc", "pharmacology", "dosage", "side_effects", "precautions"]:
    if col in df.columns:
        df[col] = df[col].apply(clean_html)

df["drug_class"] = df["drug_class"].fillna("")
df["indication"] = df["indication"].fillna("")
print(f"Loaded {len(df)} generics")

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = df.apply(lambda row: f"{row['generic_name']} {row['indication']} {row['drug_class']}", axis=1).tolist()
print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

records = []
for i, (_, row) in enumerate(df.iterrows()):
    records.append((
        int(row["id"]),
        str(row["generic_name"]),
        str(row.get("drug_class", "")),
        str(row.get("indication", "")),
        str(row.get("indication_desc", "")),
        str(row.get("pharmacology", "")),
        str(row.get("dosage", "")),
        str(row.get("side_effects", "")),
        str(row.get("precautions", "")),
        embeddings[i].tolist(),
    ))

for i in range(0, len(records), 500):
    batch = records[i : i + 500]
    execute_values(cur, "INSERT INTO generics (id, generic_name, drug_class, indication, indication_desc, pharmacology, dosage, side_effects, precautions, embedding) VALUES %s", batch)
    conn.commit()
    print(f"Inserted {min(i + 500, len(records))}/{len(records)}")

cur.close()
conn.close()
print("Done!")