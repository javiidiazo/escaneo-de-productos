FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app
RUN mkdir -p /data

ENV DJANGO_SETTINGS_MODULE=app_core.settings \
    DJANGO_DB_PATH=/data/db.sqlite3 \
    XML_LOCAL_PATH=/data/products.xml

EXPOSE 8080

CMD ["./start.sh"]
