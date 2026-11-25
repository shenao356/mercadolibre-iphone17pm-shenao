# =============================================================================
# Dockerfile de Producción - Aplicación Web Monitoreo iPhone 17 Pro Max (EA3)
# Imagen ligera basada en Python 3.12 Slim para despliegue portable en la nube
# =============================================================================
FROM python:3.12-slim

# Metadatos OCI del contenedor
LABEL maintainer="Raúl Santiago Morales Henao <shenao356@users.noreply.github.com>"
LABEL version="3.0.0"
LABEL description="Aplicación Web y API REST de monitoreo de precios iPhone 17 Pro Max - EA3 IU Digital"

# Evitar archivos .pyc y habilitar salida sin buffer para logs en la nube
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    APP_VERSION=3.0.0 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEPLOY_TARGET="Docker / Cloud Container"

WORKDIR /app

# Instalar dependencias declaradas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y datos validados
COPY scraper_mercadolibre.py deploy_dashboard.py app.py ./
COPY iphone_17_pro_max_mercadolibre.csv iphone_17_pro_max_mercadolibre.json ./
COPY docs/ ./docs/

# Exponer puerto HTTP del servicio web
EXPOSE 8000

# Healthcheck integrado para orquestadores en la nube
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" || exit 1

# Comando de inicio del servidor web WSGI
CMD ["python", "app.py"]
