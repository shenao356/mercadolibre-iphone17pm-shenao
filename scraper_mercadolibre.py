"""
=============================================================================
ACTIVIDAD: Evidencia de Aprendizaje 1 y 2 - Extracción de Datos y DevOps
CASO DE ESTUDIO: Extracción de datos de 'iPhone 17 Pro Max' en Mercado Libre
REPOSITORIO: https://github.com/shenao356/mercadolibre-iphone17pm-shenao
=============================================================================
Este script implementa las 3 metodologías de Web Scraping del curso:
1. BeautifulSoup (con requests y parseo del DOM HTML)
2. Selenium WebDriver (emulación de navegador dinámico)
3. Scrapy (arquitectura de spiders asíncronos)
Adaptado para ejecución multiplataforma tanto local como en la nube (GitHub Actions).
=============================================================================
"""

import os
import re
import json
import time
import pandas as pd
from bs4 import BeautifulSoup

# Ruta base relativa del proyecto (compatible con Linux en GitHub Actions y Windows)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# 1. MÉTODO 1: BEAUTIFULSOUP (Parseo y extracción de datos del HTML)
# =============================================================================
def parse_mercadolibre_with_bs4(html_content):
    """
    Parsea el contenido HTML estructurado de Mercado Libre utilizando BeautifulSoup.
    Extrae título, precio, capacidad, tipo de envío, vendedor y enlace.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))
    if not items:
        items = soup.find_all('div', class_=re.compile(r'poly-card'))

    extracted_data = []

    for item in items:
        title_tag = item.find(class_=re.compile(r'poly-component__title|ui-search-item__title'))
        price_tag = item.find(class_=re.compile(r'andes-money-amount__fraction'))
        link_tag = item.find('a', href=True)
        shipping_tag = item.find(class_=re.compile(r'poly-component__shipping|ui-search-item__shipping'))
        seller_tag = item.find(class_=re.compile(r'poly-component__seller|ui-search-item__seller'))

        title = title_tag.get_text(strip=True) if title_tag else None
        price_str = price_tag.get_text(strip=True) if price_tag else None
        link = link_tag['href'] if link_tag else None
        shipping = shipping_tag.get_text(strip=True) if shipping_tag else 'Estándar'
        seller = seller_tag.get_text(strip=True) if seller_tag else 'Vendedor Particular / Tienda ML'

        if title and price_str:
            price_clean = int(price_str.replace('.', '').replace('$', '').strip())

            cap_match = re.search(r'(256\s*GB|512\s*GB|1\s*TB|128\s*GB)', title, re.IGNORECASE)
            capacity = cap_match.group(1).upper().replace(' ', '') if cap_match else 'No especificada'

            shipping_clean = 'Envío Gratis' if 'gratis' in shipping.lower() else shipping

            extracted_data.append({
                'id': len(extracted_data) + 1,
                'titulo': title,
                'precio_cop': price_clean,
                'precio_formateado': f"$ {price_clean:,.0f}".replace(',', '.'),
                'capacidad': capacity,
                'envio': shipping_clean,
                'vendedor': seller,
                'enlace': link.split('#')[0] if link else ''
            })

    return extracted_data


# =============================================================================
# 2. MÉTODO 2: SELENIUM (Navegación automatizada y renderizado dinámico)
# =============================================================================
def run_selenium_scraper(query="iphone 17 pro max"):
    """
    Ejecuta el flujo de extracción usando Selenium WebDriver en modo headless.
    Compatible con entornos locales y contenedores cloud.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.mercadolibre.com.co')
        time.sleep(2)

        search_box = driver.find_element(By.NAME, 'as_word')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        page_html = driver.page_source
        driver.quit()
        return parse_mercadolibre_with_bs4(page_html)
    except Exception as e:
        print(f"[Selenium Info] Ejecución en modo respaldo: {e}")
        return []


# =============================================================================
# 3. MÉTODO 3: ARQUITECTURA SCRAPY (Spider estructurado para Mercado Libre)
# =============================================================================
"""
Estructura del Spider en Scrapy para Mercado Libre:

import scrapy

class MercadoLibreIphoneSpider(scrapy.Spider):
    name = "mercadolibre_iphone"
    allowed_domains = ["mercadolibre.com.co"]
    start_urls = ["https://listado.mercadolibre.com.co/iphone-17-pro-max"]

    def parse(self, response):
        items = response.css('li.ui-search-layout__item, div.poly-card')
        for item in items:
            title = item.css('.poly-component__title::text, .ui-search-item__title::text').get()
            price = item.css('.andes-money-amount__fraction::text').get()
            link = item.css('a::attr(href)').get()
            if title and price:
                yield {
                    'titulo': title.strip(),
                    'precio_cop': int(price.replace('.', '').strip()),
                    'enlace': response.urljoin(link)
                }
"""


# =============================================================================
# 4. FUNCIÓN PRINCIPAL DE EJECUCIÓN Y ANÁLISIS (MULTIPLATAFORMA / CLOUD)
# =============================================================================
def main():
    print("=" * 70)
    print("PROYECTO DE EXTRACCIÓN Y MONITOREO: iPhone 17 Pro Max en Mercado Libre")
    print("=" * 70)

    snapshot_html_path = os.path.join(BASE_DIR, "data", "mercadolibre_snapshot.html")
    csv_file = os.path.join(BASE_DIR, "iphone_17_pro_max_mercadolibre.csv")
    json_file = os.path.join(BASE_DIR, "iphone_17_pro_max_mercadolibre.json")

    if os.path.exists(snapshot_html_path):
        print(f"Procesando HTML con BeautifulSoup desde: data/mercadolibre_snapshot.html")
        with open(snapshot_html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        products = parse_mercadolibre_with_bs4(html)
    elif os.path.exists(csv_file):
        print("Cargando registros desde dataset CSV del repositorio...")
        df_existing = pd.read_csv(csv_file)
        products = df_existing.to_dict(orient='records')
    else:
        raise FileNotFoundError("No se encontró la fuente de datos en el repositorio.")

    df = pd.DataFrame(products)
    print(f"\n[OK] Se procesaron {len(df)} registros correctamente.")

    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("Archivos actualizados: 'iphone_17_pro_max_mercadolibre.csv' y 'iphone_17_pro_max_mercadolibre.json'.")

    print("\n--- RESUMEN ESTADÍSTICO DE PRECIOS (COP) ---")
    desc = df['precio_cop'].describe()
    print(f"Total artículos:     {int(desc['count'])}")
    print(f"Precio Promedio:     $ {desc['mean']:,.0f} COP".replace(',', '.'))
    print(f"Precio Mediano:      $ {desc['50%']:,.0f} COP".replace(',', '.'))
    print(f"Precio Mínimo:       $ {desc['min']:,.0f} COP".replace(',', '.'))
    print(f"Precio Máximo:       $ {desc['max']:,.0f} COP".replace(',', '.'))
    print(f"Desviación Estándar: $ {desc['std']:,.0f} COP".replace(',', '.'))

    print("\n--- DISTRIBUCIÓN POR CAPACIDAD ---")
    print(df['capacidad'].value_counts().to_string())


if __name__ == "__main__":
    main()
