#!/usr/bin/env bash
set -euo pipefail

APP="suiza-product-scanner"

if ! command -v fly >/dev/null 2>&1; then
  echo "flyctl no está instalado. Instalalo desde https://fly.io/docs/hands-on/installing/" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Este script requiere jq (brew install jq)." >&2
  exit 1
fi

fly scale count 1 --app "$APP"

printf 'Esperando a que la API esté lista'
for _ in {1..24}; do
  passing=$(fly status --app "$APP" --json | jq -r '.MachineStatuses[0].ChecksPassing // 0')
  if [[ "$passing" != "0" ]]; then
    echo -e "\nAPI lista en Fly.io"
    exit 0
  fi
  printf '.'
  sleep 5
 done

echo -e "\nAdvertencia: la API no pasó el healthcheck todavía. Revisá con 'fly status'."
exit 1
