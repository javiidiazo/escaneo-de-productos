#!/bin/bash
set -euo pipefail

if [[ -n "${SFTP_PRIVATE_KEY_B64:-}" ]]; then
  KEY_PATH="${SFTP_KEY_PATH:-/data/sftp_key.pem}"
  mkdir -p "$(dirname "$KEY_PATH")"
  echo "$SFTP_PRIVATE_KEY_B64" | base64 -d > "$KEY_PATH"
  chmod 600 "$KEY_PATH"
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec gunicorn app_core.wsgi --bind 0.0.0.0:${PORT:-8080}
