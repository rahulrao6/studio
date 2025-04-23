FROM python:3.11-slim

WORKDIR /app


# Install required build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install spacy && python -m spacy download en_core_web_lg

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
