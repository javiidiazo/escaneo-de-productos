# Frontend - Escáner de productos

Aplicación React (Vite) que permite escanear códigos de barras desde un dispositivo móvil y consultar la API de productos.

## Scripts principales

- `npm install` para instalar dependencias.
- `npm run dev` para levantar el entorno de desarrollo en `http://localhost:5173`.
- `npm run build` para generar el bundle listo para producción.
- `npm run preview` para previsualizar el build de producción.

La configuración de Vite (`vite.config.js`) incluye un proxy a `http://localhost:8000` para redirigir las llamadas a `/api` hacia el backend de Django durante el desarrollo.

## Variables de entorno

Usamos dos variables (ver `.env.example`):

- `VITE_API_URL`: endpoint de la API en producción. Por defecto cae en `/api` para desarrollo local.
- `DEPLOY_BASE`: ruta base pública para el build. GitHub Pages requiere `/<nombre-del-repo>/`.

Podés crear `.env.local` para desarrollo y `.env.production` con los valores reales antes de hacer `npm run build`.

## Deploy a GitHub Pages

El workflow `frontend-deploy.yml` compila el proyecto y publica `dist/` en la rama `gh-pages`. Antes de ejecutarlo configurá el secret `VITE_API_URL` con la URL pública del backend y habilitá GitHub Pages en las settings del repositorio. Ajustá `DEPLOY_BASE` desde el workflow o con un secret si usás un dominio personalizado.
