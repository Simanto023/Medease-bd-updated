import pandas as pd
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "medease_db"),
    "user": os.getenv("POSTGRES_USER", "medease"),
    "password": os.getenv("POSTGRES_PASSWORD", "medease123"),
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Get medicines with their generic info
cur.execute("""
    SELECT m.brand_name, m.generic_name, m.company, m.strength, m.form, m.price_bdt, m.package_info,
           g.indication, g.indication_desc, g.dosage, g.side_effects, g.drug_class
    FROM medicines m
    LEFT JOIN generics g ON m.generic_name = g.generic_name
    WHERE m.price_bdt > 0
    LIMIT 5000
""")

qa_pairs = []
for row in cur.fetchall():
    brand, generic, company, strength, form, price, package, indication, ind_desc, dosage, side_effects, drug_class = row
    
    price_str = f"৳{price:.2f}" if price else "Price not available"
    strength_str = strength or "N/A"
    form_str = form or "N/A"
    
    # Q/A about the medicine
    if brand:
        qa_pairs.append({
            "instruction": "You are MedEase BD, a medicine information assistant for Bangladesh. Answer using the provided information.",
            "input": f"What is {brand}?",
            "output": f"{brand} contains {generic} {strength_str}. It is manufactured by {company}. Form: {form_str}. Price: {price_str}."
        })
        
        qa_pairs.append({
            "instruction": "You are MedEase BD, a medicine information assistant for Bangladesh. Answer using the provided information.",
            "input": f"What is the price of {brand}?",
            "output": f"{brand} ({generic}, {strength_str}) by {company} costs {price_str}."
        })
    
    # Q/A about usage if indication available
    if indication and generic:
        qa_pairs.append({
            "instruction": "You are MedEase BD, a medicine information assistant for Bangladesh. Answer using the provided information.",
            "input": f"What is {generic} used for?",
            "output": f"{generic} is used for {indication}. {ind_desc[:200] if ind_desc else ''}".strip()
        })
    
    if dosage and generic:
        qa_pairs.append({
            "instruction": "You are MedEase BD, a medicine information assistant for Bangladesh. Answer using the provided information.",
            "input": f"What is the dosage of {generic}?",
            "output": f"Dosage of {generic}: {dosage[:300]}"
        })

cur.close()
conn.close()

# Save as JSON
with open("data/qa_training_data.json", "w", encoding="utf-8") as f:
    json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

print(f"Generated {len(qa_pairs)} Q/A pairs")
print("Saved to data/qa_training_data.json")
