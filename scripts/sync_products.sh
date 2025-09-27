#!/usr/bin/env bash
set -euo pipefail

APP="suiza-product-scanner"
REGION="gru"
VOLUME="products_data"
MEMORY_MB="2048"

if ! command -v fly >/dev/null 2>&1; then
  echo "flyctl no está instalado. Instalalo desde https://fly.io/docs/hands-on/installing/" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Este script requiere jq (brew install jq)." >&2
  exit 1
fi

IMAGE=$(fly machines list --app "$APP" --json | jq -r '.[0].ImageRef')
if [[ -z "$IMAGE" || "$IMAGE" == "null" ]]; then
  echo "No pude obtener la imagen actual de la app. Asegurate de haber hecho al menos un deploy." >&2
  exit 1
fi

echo "Levantando máquina temporal para sincronizar productos..."
fly machines run "$IMAGE" \
  --app "$APP" \
  --region "$REGION" \
  --mount source="$VOLUME",target=/data \
  --vm-memory "$MEMORY_MB" \
  --command "/bin/bash" -- \
    -lc "cd /app && python manage.py sync_products_from_sftp" && \
  echo "Sincronización completada"
