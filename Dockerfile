FROM python:3.10-slim

# Gerekli sistem araçlarını kur
RUN apt-get update && apt-get install -y \
    libgdiplus \
    libicu-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Aspose'un aradığı libssl1.1 paketini manuel indir ve sisteme zorla tanıt
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb \
    && dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb \
    && rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb

WORKDIR /app

# Bellek ve Dil optimizasyonları
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true
ENV MALLOC_ARENA_MAX=2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port ayarı
ENV PORT=10000
EXPOSE 10000

# Gunicorn'u en kararlı modda başlat (Tek worker, yüksek timeout)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1", "--threads", "4", "--worker-class", "gthread", "app:app"]
