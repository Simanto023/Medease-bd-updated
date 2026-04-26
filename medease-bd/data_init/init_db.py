import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import re
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


def extract_price(package_str):
    """Extract price from package container string like '100 ml bottle: ৳ 40.12'"""
    if pd.isna(package_str) or not package_str:
        return None
    match = re.search(r'৳\s*([\d,.]+)', str(package_str))
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def clean_html(html_str):
    """Strip HTML tags from text"""
    if pd.isna(html_str) or not html_str:
        return ""
    return re.sub(r'<[^>]+>', ' ', str(html_str)).strip()


def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

        cur.execute("DROP TABLE IF EXISTS medicines CASCADE")
        cur.execute("DROP TABLE IF EXISTS generics CASCADE")

        cur.execute("""
            CREATE TABLE medicines (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                brand_name VARCHAR(500) NOT NULL,
                type VARCHAR(50),
                generic_name TEXT NOT NULL,
                company VARCHAR(500) NOT NULL,
                strength VARCHAR(200),
                form VARCHAR(100),
                package_info VARCHAR(500),
                price_bdt FLOAT,
                embedding vector(384)
            )
        """)

        cur.execute("""
            CREATE TABLE generics (
                id INTEGER PRIMARY KEY,
                generic_name TEXT NOT NULL,
                drug_class VARCHAR(500),
                indication VARCHAR(1000),
                indication_desc TEXT,
                pharmacology TEXT,
                dosage TEXT,
                side_effects TEXT,
                precautions TEXT,
                embedding vector(384)
            )
        """)

        cur.execute("CREATE INDEX idx_medicines_brand ON medicines USING btree (brand_name)")
        cur.execute("CREATE INDEX idx_medicines_company ON medicines USING btree (company)")
        cur.execute("CREATE INDEX idx_generics_name ON generics USING btree (generic_name)")
        conn.commit()
        print("✅ Tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def load_medicines():
    data_dir = "data"
    df = pd.read_csv(os.path.join(data_dir, "medicine.csv"))
    print(f"Loaded {len(df)} medicine records")

    df = df.rename(columns={
        "brand name": "brand_name",
        "type": "type",
        "generic": "generic_name",
        "manufacturer": "company",
        "strength": "strength",
        "dosage form": "form",
        "package container": "package_info",
    })

    df["price_bdt"] = df["package_info"].apply(extract_price)
    df["strength"] = df["strength"].fillna("").astype(str)
    df["form"] = df["form"].fillna("").astype(str)
    df["type"] = df["type"].fillna("allopathic").astype(str)
    df["package_info"] = df["package_info"].fillna("").astype(str)
    df = df.dropna(subset=["brand_name", "generic_name", "company"])
    df = df.drop_duplicates(subset=["brand_name", "generic_name", "company"])

    print(f"✅ Cleaned medicines: {len(df)} records")
    return df


def load_generics():
    data_dir = "data"
    df = pd.read_csv(os.path.join(data_dir, "generic.csv"))
    print(f"Loaded {len(df)} generic records")

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

    print(f"✅ Cleaned generics: {len(df)} records")
    return df


def generate_embeddings(texts_list):
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Generating embeddings for {len(texts_list)} items...")
    embeddings = model.encode(texts_list, show_progress_bar=True, batch_size=32)
    return embeddings


def seed_medicines(df):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        texts = df.apply(
            lambda row: f"{row['brand_name']} {row['generic_name']} {row['company']} {row['strength']} {row['form']}",
            axis=1,
        ).tolist()
        embeddings = generate_embeddings(texts)

        records = []
        for i, (_, row) in enumerate(df.iterrows()):
            records.append((
                str(row["brand_name"]),
                str(row["type"]),
                str(row["generic_name"]),
                str(row["company"]),
                str(row["strength"]),
                str(row["form"]),
                str(row["package_info"]),
                row["price_bdt"] if pd.notna(row["price_bdt"]) else None,
                embeddings[i].tolist(),
            ))

        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            execute_values(
                cur,
                "INSERT INTO medicines (brand_name, type, generic_name, company, strength, form, package_info, price_bdt, embedding) VALUES %s",
                batch,
            )
            conn.commit()
            print(f"Inserted {min(i + batch_size, len(records))}/{len(records)} medicine records")

        print(f"✅ Successfully seeded {len(records)} medicines")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding medicines: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def seed_generics(df):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        texts = df.apply(
            lambda row: f"{row['generic_name']} {row['indication']} {row['drug_class']}",
            axis=1,
        ).tolist()
        embeddings = generate_embeddings(texts)

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

        batch_size = 500
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            execute_values(
                cur,
                "INSERT INTO generics (id, generic_name, drug_class, indication, indication_desc, pharmacology, dosage, side_effects, precautions, embedding) VALUES %s",
                batch,
            )
            conn.commit()
            print(f"Inserted {min(i + batch_size, len(records))}/{len(records)} generic records")

        print(f"✅ Successfully seeded {len(records)} generics")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding generics: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def main():
    print("🚀 Starting MedEase BD Database Initialization with full dataset...")
    wait_for_db()
    create_tables()

    print("\n📂 Loading medicines...")
    med_df = load_medicines()

    print("\n📂 Loading generics...")
    gen_df = load_generics()

    print("\n💊 Seeding medicines...")
    seed_medicines(med_df)

    print("\n🧬 Seeding generics...")
    seed_generics(gen_df)

    print("\n✅✅✅ Database initialization complete! ✅✅✅")


if __name__ == "__main__":
    main()