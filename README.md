# Web App de Escaneo de Productos

Este repositorio contiene la base del proyecto descrito en el roadmap: backend en Django + DRF encargado de procesar el XML de productos y una SPA en React capaz de leer códigos de barras desde la cámara del teléfono.

## Estructura

```
Escaneo de productos suiza/
├── backend/
│   ├── app_core/           # Proyecto Django (settings y URLs)
│   ├── products/           # App dedicada al catálogo de productos
│   ├── data/               # Directorio para el XML descargado
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── api/
        ├── components/
        ├── pages/
        └── styles/
```

## Backend (Django + DRF)

- `products/models.py`: modelo `Product` con los campos necesarios.
- `products/serializers.py`: serializador DRF para exponer el producto como JSON.
- `products/views.py`: endpoints `/api/health` y `/api/products/<barcode>`.
- `products/xml_loader.py`: parser y rutina `import_products` para transformar el XML en registros.
- `products/sftp_client.py`: helper con Paramiko para bajar el XML por SFTP (usa variables de entorno).
- `products/management/commands/sync_products_from_sftp.py`: comando `python manage.py sync_products_from_sftp` que descarga e importa el feed.
- Ajustes en `app_core/settings.py` para DRF, rutas y configuración del feed (`PRODUCT_FEED_LOCAL_PATH`).

### Cómo ejecutar en desarrollo

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Para probar el comando de sincronización usando un XML local:

```bash
python manage.py sync_products_from_sftp --skip-download --local-path data/products.xml
```

> Nota: se incluye `.env.example` con las variables de entorno necesarias.

#### Sincronización vía SFTP

1. Copiá la clave privada que recibiste a la ruta indicada en `SFTP_KEY_PATH` (por defecto `/Users/Usuario1/Downloads/suiza_key.pem`).
2. Configurá el archivo `.env` (ya creado en la raíz del proyecto) con `SFTP_HOST`, `SFTP_USER` y las rutas remota/local reales.
3. Activá el entorno virtual y exportá las variables:

   ```bash
   cd backend
   source .venv/bin/activate
   export $(cat ../.env | xargs)
   ```

4. Ejecutá en un shell de Django para validar solo la descarga:

   ```bash
   python manage.py shell
   >>> from products.sftp_client import download_xml
   >>> download_xml()
   ```

   El XML se guardará en `backend/data/products.xml` (o la ruta que definas en `XML_LOCAL_PATH`).

5. Una vez descargado, importá y actualizá la base local:

   ```bash
   python manage.py sync_products_from_sftp --skip-download --local-path "$XML_LOCAL_PATH"
   ```

## Frontend (React + Vite)

- Router básico con dos rutas: `/` (scanner) y `/p/:barcode` (detalle de producto).
- `BarcodeScanner.jsx` utiliza `@zxing/library` para acceder a la cámara y detectar códigos.
- `ProductPage.jsx` consulta la API `/api/products/<barcode>` y renderiza el resultado vía `ProductCard`.
- `vite.config.js` expone un proxy para `/api` → `http://localhost:8000` durante el desarrollo.

### Cómo ejecutar en desarrollo

```bash
cd frontend
npm install
npm run dev
```

La aplicación quedará disponible en `http://localhost:5173`.

### Variables de entorno del frontend

En `frontend/.env.example` vas a encontrar dos variables:

- `VITE_API_URL`: URL completa del backend en producción (`https://tu-dominio.com/api`).
- `DEPLOY_BASE`: ruta base pública del build (para GitHub Pages será `/<nombre-del-repo>/`).

Copiá ese archivo a `.env.local` para desarrollo o completá los valores desde el workflow (ver más abajo).

### Deploy automático a GitHub Pages

El workflow `.github/workflows/frontend-deploy.yml` compila la SPA y la publica en la rama `gh-pages` cada vez que haces push a `main`. Antes de activarlo:

1. Creá el repositorio en GitHub, agregá este proyecto como remoto y hacé push (`git remote add origin …`, `git push -u origin main`).
2. En GitHub → *Settings → Secrets and variables → Actions* agregá el secret `VITE_API_URL` con la URL pública de tu backend (por ejemplo `https://api.midominio.com/api`).
3. En *Settings → Pages* elegí “Deploy from branch” con `gh-pages` / root.

El workflow fija automáticamente `DEPLOY_BASE` a `/<nombre-del-repositorio>/`, que es lo que espera GitHub Pages. Si usás un dominio personalizado, podés añadir un secret opcional `DEPLOY_BASE` con `/` y editar el workflow para exportarlo.

> GitHub Pages sólo sirve contenido estático. El backend Django debe desplegarse en otro servicio (Fly.io, Railway, Render, EC2, etc.) y exponer públicamente `/api`. Ajustá CORS para permitir el dominio donde publiques la SPA.

### Deploy del backend en Fly.io

El repositorio incluye un `Dockerfile` (`backend/Dockerfile`), un script de arranque (`backend/start.sh`) y un `fly.toml` base para subir Django a [Fly.io](https://fly.io/).

1. **Instalá la CLI** (`curl -L https://fly.io/install.sh | sh`) y autenticá la sesión con `fly auth login`.
2. **Editá `fly.toml`**: cambiá `app = "escaneo-productos"` por un nombre único y, si hace falta, ajustá `primary_region`.
3. **Creá la app y el volumen**:

   ```bash
   fly apps create <tu-app>
   fly volumes create products_data --app <tu-app> --size 1 --region <region>
   ```

4. **Definí los secretos** (Fly los encripta):

   ```bash
   fly secrets set \
     DJANGO_SECRET_KEY="$(openssl rand -base64 48)" \
     DJANGO_ALLOWED_HOSTS="tu-dominio.com" \
     DJANGO_DB_PATH=/data/db.sqlite3 \
     SFTP_HOST=35.174.226.128 \
     SFTP_PORT=22 \
     SFTP_USER=ubuntu \
     SFTP_REMOTE_PATH=/home/ubuntu/articulos/xmlArticulosSuizaOutdoor.xml \
     XML_LOCAL_PATH=/data/products.xml \
     SFTP_KEY_PATH=/data/suiza_key.pem \
     SFTP_PRIVATE_KEY_B64="$(base64 < ~/Downloads/suiza_key.pem | tr -d '\n')"
   ```

   Si preferís Postgres administrado, agregá `DATABASE_URL` (Fly Postgres o externos) y remové `DJANGO_DB_PATH`.

5. **Deploy**:

   ```bash
   fly deploy
   ```

   El `release_command` ejecuta las migraciones y el volumen `products_data` guarda `db.sqlite3` + `products.xml`.

6. **Sincronización periódica**: Fly permite programar máquinas. Buscá el `IMAGE` de la última release (`fly machines list --app <tu-app>`) y creá una máquina cron que ejecute el comando cada 30 minutos:

   ```bash
   fly machine run \
     --app <tu-app> \
     --region <region> \
     --schedule "*/30 * * * *" \
     --select "volume=products_data" \
     <imagen> \
     -- /bin/bash -lc "python manage.py sync_products_from_sftp"
   ```

   Para sincronizaciones puntuales:

   ```bash
   fly ssh console --app <tu-app> --command "python manage.py sync_products_from_sftp"
   ```

> Recordá usar la URL del backend (`https://<tu-app>.fly.dev/api`) en `VITE_API_URL` para que la SPA publicada consuma la API correcta.

## Próximos pasos sugeridos

1. Conectar el comando `sync_products_from_sftp` con el servidor SFTP real y validar el esquema del XML productivo.
2. Añadir autenticación básica (token/API key) o rate limiting si hace falta proteger `/api/products/*`.
3. Implementar caching en la vista DRF y, si se requiere, paginar un futuro endpoint de búsqueda.
4. Convertir la SPA en PWA (manifest + service worker) para el modo kiosco/offline.
5. Añadir métricas/eventos (por ejemplo con Google Analytics 4 o Plausible) para medir uso del escáner.
6. Automatizar deploy: contenedores Docker + Nginx/Gunicorn o la infraestructura elegida.
