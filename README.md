# Proyecto Web Scraping y DevOps: iPhone 17 Pro Max en Mercado Libre

Repositorio de las **Evidencias de Aprendizaje 1 y 2** de la materia **Análisis y Herramientas de Extracción de Datos** (IU Digital de Antioquia).

* **Repositorio:** `https://github.com/shenao356/mercadolibre-iphone17pm-shenao`
* **Artículo analizado:** Apple iPhone 17 Pro Max (48 publicaciones en Mercado Libre Colombia)

---

## 1. Descripción general

En la **Actividad 1** se realizó la extracción de datos (*Web Scraping*) de las publicaciones del **iPhone 17 Pro Max** en Mercado Libre utilizando Python (**BeautifulSoup**, **Selenium** y **Scrapy**), guardando los datos limpios en formato CSV y JSON.

En esta **Actividad 2**, continuamos el proyecto aplicando **Git**, **GitHub** y un flujo de trabajo **DevOps (CI/CD)** con **GitHub Actions** para automatizar la revisión del código, las pruebas automáticas y el despliegue de un reporte web.

---

## 2. Archivos principales del proyecto

* `scraper_mercadolibre.py`: Script en Python que extrae y procesa la información de los 48 celulares iPhone 17 Pro Max.
* `iphone_17_pro_max_mercadolibre.csv` y `.json`: Bases de datos con los resultados obtenidos.
* `tests/test_scraper.py`: Pruebas automáticas para verificar que los precios, capacidades y enlaces se extraigan sin errores.
* `deploy_dashboard.py` y `docs/index.html`: Generador del reporte web con el resumen de precios y tabla de productos.
* `.github/workflows/ci_cd_pipeline.yml`: Flujo de automatización en GitHub Actions que ejecuta las pruebas y el despliegue en cada cambio.
* `Apellido_Nombre_Analizando_EA1.ipynb` y `Apellido_Nombre_Optimizando_EA2.ipynb`: Cuadernos de Jupyter de las entregas 1 y 2.

---

## 3. Cómo ejecutar el proyecto

```bash
# 1. Instalar librerías
pip install -r requirements.txt

# 2. Correr las pruebas automáticas
python -m unittest discover -s tests -v

# 3. Ejecutar el scraper y resumen estadístico
python scraper_mercadolibre.py

# 4. Actualizar el tablero web
python deploy_dashboard.py
```

---

## 4. Resumen de resultados del iPhone 17 Pro Max

* **Total de publicaciones analizadas:** 48
* **Precio promedio:** `$ 4.917.059 COP`
* **Precio mediano:** `$ 4.624.500 COP`
* **Precio mínimo / máximo:** `$ 2.667.777 COP` / `$ 9.999.000 COP`
* **Capacidades encontradas:** 256 GB (35), 512 GB (8), 1 TB (1), No especificada (4)
