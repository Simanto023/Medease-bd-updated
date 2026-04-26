import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from dotenv import load_dotenv
import time

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "medease_db"),
    "user": os.getenv("POSTGRES_USER", "medease"),
    "password": os.getenv("POSTGRES_PASSWORD", "medease123"),
}


def wait_for_db():
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("✅ Database is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
    raise Exception("Could not connect to database")


def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                brand_name VARCHAR(500) NOT NULL,
                generic_name TEXT NOT NULL,
                company VARCHAR(500) NOT NULL,
                strength VARCHAR(200),
                form VARCHAR(100),
                price_bdt FLOAT,
                embedding vector(384)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_medicines_brand ON medicines USING btree (brand_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_medicines_company ON medicines USING btree (company)")
        conn.commit()
        print("✅ Tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def load_and_clean_data():
    """Load from Excel or CSV — auto-detects which file is present."""
    data_dir = "data"
    df = None

    # Try Excel first, then CSV
    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            print(f"📂 Loading Excel file: {filename}")
            df = pd.read_excel(filepath, engine="openpyxl")
            break
        elif filename.endswith(".csv"):
            print(f"📂 Loading CSV file: {filename}")
            df = pd.read_csv(filepath)
            break

    if df is None:
        raise FileNotFoundError("No .xlsx, .xls, or .csv file found in data/ folder")

    print(f"Loaded {len(df)} records")
    print(f"Columns found: {list(df.columns)}")

    # Normalise column names to lowercase with underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Map common column name variations to expected names
    rename_map = {
        "brand": "brand_name",
        "brandname": "brand_name",
        "brand_names": "brand_name",
        "generic": "generic_name",
        "genericname": "generic_name",
        "manufacturer": "company",
        "company_name": "company",
        "dosage_form": "form",
        "dosageform": "form",
        "drug_form": "form",
        "price": "price_bdt",
        "price_(bdt)": "price_bdt",
        "mrp": "price_bdt",
    }
    df = df.rename(columns=rename_map)

    # Ensure required columns exist
    required = ["brand_name", "generic_name", "company"]
    for col in required:
        if col not in df.columns:
            # Try to find a close match
            print(f"⚠️  Column '{col}' not found. Available: {list(df.columns)}")
            raise ValueError(f"Required column '{col}' missing from data file")

    # Add optional columns if missing
    for col in ["strength", "form", "price_bdt"]:
        if col not in df.columns:
            df[col] = ""

    df = df.dropna(subset=["brand_name", "generic_name", "company"])
    df = df.drop_duplicates(subset=["brand_name", "generic_name", "company"])
    df["strength"] = df["strength"].fillna("").astype(str)
    df["form"] = df["form"].fillna("").astype(str)
    df["price_bdt"] = pd.to_numeric(df["price_bdt"], errors="coerce").fillna(0)

    print(f"✅ Cleaned data: {len(df)} records")
    return df


def generate_embeddings(df):
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = df.apply(
        lambda row: f"{row['brand_name']} {row['generic_name']} {row['company']} {row['strength']} {row['form']}",
        axis=1,
    ).tolist()
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    print(f"✅ Generated {len(embeddings)} embeddings")
    return embeddings


def seed_database(df, embeddings):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM medicines")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"Database already has {count} medicines. Skipping seed.")
            return

        records = []
        for i, (_, row) in enumerate(df.iterrows()):
            records.append((
                str(row["brand_name"]),
                str(row["generic_name"]),
                str(row["company"]),
                str(row["strength"]),
                str(row["form"]),
                float(row["price_bdt"]),
                embeddings[i].tolist(),
            ))

        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            execute_values(
                cur,
                "INSERT INTO medicines (brand_name, generic_name, company, strength, form, price_bdt, embedding) VALUES %s",
                batch,
            )
            conn.commit()
            print(f"Inserted {min(i + batch_size, len(records))}/{len(records)} records")

        print(f"✅ Successfully seeded {len(records)} medicines")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def main():
    print("🚀 Starting MedEase BD Database Initialization...")
    wait_for_db()
    create_tables()
    df = load_and_clean_data()
    embeddings = generate_embeddings(df)
    seed_database(df, embeddings)
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    main()
