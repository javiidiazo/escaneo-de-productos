#!/usr/bin/env bash
set -euo pipefail

APP="suiza-product-scanner"

if ! command -v fly >/dev/null 2>&1; then
  echo "flyctl no está instalado. Instalalo desde https://fly.io/docs/hands-on/installing/" >&2
  exit 1
fi

fly scale count 0 --app "$APP"

echo "API detenida en Fly.io"
