FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pandas \
    numpy \
    openpyxl \
    psycopg2-binary \
    sentence-transformers \
    python-dotenv \
    scikit-learn

COPY init_db.py .
COPY data/ ./data/

CMD ["python", "init_db.py"]