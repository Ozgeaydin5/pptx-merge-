FROM python:3.10-slim

# Gerekli sistem kütüphanelerini ve eski libssl desteğini kur
RUN apt-get update && apt-get install -y \
    libgdiplus \
    libicu-dev \
    wget \
    && wget http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb \
    && dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb \
    && rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Bellek ve Dil ayarları
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true
ENV MALLOC_ARENA_MAX=2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tek bir işe odaklansın, kütüphaneyi yormasın
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1", "app:app"]
