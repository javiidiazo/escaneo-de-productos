# Stage 1: build the React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ENV STATIC_BASE_URL=/static/frontend/
ENV VITE_API_URL=/api
RUN npm run build

# Stage 2: build the Django backend
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
COPY --from=frontend-build /app/frontend/dist /app/frontend_dist
RUN mkdir -p /app/static/frontend /app/templates/frontend /data \
    && cp -r /app/frontend_dist/assets /app/static/frontend/ \
    && cp /app/frontend_dist/index.html /app/templates/frontend/index.html

ENV DJANGO_SETTINGS_MODULE=app_core.settings \
    DJANGO_DB_PATH=/data/db.sqlite3 \
    XML_LOCAL_PATH=/data/products.xml \
    STATIC_BASE_URL=/static/frontend/ \
    PORT=8080

EXPOSE 8080

CMD ["./start.sh"]
