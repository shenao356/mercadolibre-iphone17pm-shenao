# Proyecto Web Scraping y DevOps: iPhone 17 Pro Max en Mercado Libre

Repositorio de las **Evidencias de Aprendizaje 1 y 2** de la materia **Programación para Análisis de Datos - PREICA2602B020048** (Institución Universitaria Digital de Antioquia - IU Digital).

* **Integrante:** Raúl Santiago Morales Henao
* **Docente:** Andrés Felipe Palacio
* **Repositorio:** `https://github.com/shenao356/mercadolibre-iphone17pm-shenao`
* **Tablero Web Desplegado (GitHub Pages):** `https://shenao356.github.io/mercadolibre-iphone17pm-shenao/`
* **Artículo analizado:** Apple iPhone 17 Pro Max (48 publicaciones en Mercado Libre Colombia)

---

## 1. Descripción general

En la **Evidencia de aprendizaje 1 (S30)** se realizó la extracción de datos (*Web Scraping*) de las publicaciones del **iPhone 17 Pro Max** en Mercado Libre utilizando Python (**BeautifulSoup**, **Selenium** y **Scrapy**), guardando los datos limpios en formato CSV y JSON.

En esta **Evidencia de aprendizaje 2 (S35)**, continuamos el proyecto aplicando **Git**, **GitHub** y un flujo de trabajo **DevOps (CI/CD)** con **GitHub Actions** para automatizar la revisión del código, las pruebas unitarias automáticas y el despliegue continuo del tablero web y la API JSON en la nube.

---

## 2. Archivos y documentos principales del repositorio

* `Morales_Henao_Raul_Santiago_Optimizando_EA2.pdf`: Trabajo escrito en PDF de la Entrega 2 con el formato institucional APA 7ª edición de la IU Digital.
* `scraper_mercadolibre.py`: Script en Python que extrae y procesa la información de los 48 celulares iPhone 17 Pro Max (diferenciando el precio actual `div.poly-price__current` del precio anterior tachado `<s>`).
* `iphone_17_pro_max_mercadolibre.csv` y `.json`: Bases de datos con los 48 productos extraídos.
* `tests/test_scraper.py`: Suite de 6 pruebas unitarias automáticas (`unittest`) para verificar que los precios reales, descuentos, capacidades y enlaces se extraigan sin errores.
* `deploy_dashboard.py`, `docs/index.html` y `docs/api/iphone17_data.json`: Generador y archivos del tablero web y API JSON publicados en GitHub Pages.
* `workflows/ci_cd_pipeline.yml`: Configuración del flujo de integración y despliegue continuo (CI/CD) en GitHub Actions.

---

## 3. Cómo ejecutar el proyecto

```bash
# 1. Instalar librerías
pip install -r requirements.txt

# 2. Correr las 6 pruebas unitarias automáticas
python -m unittest discover -s tests -v

# 3. Ejecutar el scraper y resumen estadístico
python scraper_mercadolibre.py

# 4. Actualizar el tablero web y el archivo JSON de despliegue
python deploy_dashboard.py
```

---

## 4. Resumen de resultados del iPhone 17 Pro Max (Precios reales de venta)

* **Total de publicaciones analizadas:** 48
* **Precio promedio:** `$ 4.776.156 COP`
* **Precio mediano:** `$ 4.600.000 COP`
* **Precio mínimo / máximo:** `$ 2.667.777 COP` / `$ 7.990.000 COP`
* **Capacidades encontradas:** 256 GB (35), 512 GB (8), 1 TB (1), No especificada (4)
