FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ make libpq-dev libopenblas-dev && rm -rf /var/lib/apt/lists/*
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
ENV FORCE_CMAKE=1
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN mkdir -p app/models
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]