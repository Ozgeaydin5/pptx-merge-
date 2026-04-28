FROM python:3.10-slim

# Aspose için hayati olan kütüphaneleri kuruyoruz
RUN apt-get update && apt-get install -y \
    libgdiplus \
    libicu-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render'ın dinamik portuna uyum sağla
ENV PORT=10000
EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1", "app:app"]
