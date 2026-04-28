# Aspose için gerekli olan tüm bağımlılıkları barındıran temel imaj
FROM python:3.10-slim

# Sistem bağımlılıklarını kur (libssl ve ICU dahil)
RUN apt-get update && apt-get install -y \
    libgdiplus \
    libicu-dev \
    libssl-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Kütüphaneleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodları kopyala
COPY . .

# Render'ın portuna uyum sağla
ENV PORT=10000
EXPOSE 10000

# Gunicorn ile başlat
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1", "app:app"]
