FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    apt-get install -y curl && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m nltk.downloader -d /usr/local/nltk_data stopwords wordnet && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV NLTK_DATA=/usr/local/nltk_data

COPY . .

RUN chmod +x entrypoint.sh

CMD ["python", "chat_cli.py"]

