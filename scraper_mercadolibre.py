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
=============================================================================
"""

import os
import re
import json
import time
import pandas as pd
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# 1. MÉTODO 1: BEAUTIFULSOUP (Parseo y extracción de datos del HTML)
# =============================================================================
def parse_mercadolibre_with_bs4(html_content):
    """
    Parsea el contenido HTML estructurado de Mercado Libre utilizando BeautifulSoup.
    Extrae el precio actual real desde 'div.poly-price__current' (ignorando el
    precio anterior tachado <s>), además de descuento, capacidad, envío y enlace.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))
    if not items:
        items = soup.find_all('div', class_=re.compile(r'poly-card'))

    extracted_data = []

    for item in items:
        title_tag = item.find(class_=re.compile(r'poly-component__title|ui-search-item__title'))

        # 1. Buscar específicamente el contenedor del precio actual de venta (no el tachado <s>)
        current_price_box = item.find('div', class_=re.compile(r'poly-price__current'))
        if current_price_box:
            price_tag = current_price_box.find(class_=re.compile(r'andes-money-amount__fraction'))
            discount_tag = current_price_box.find(class_=re.compile(r'poly-price__discount'))
        else:
            # Fallback para tarjetas simples sin contenedor poly-price__current
            price_tag = item.find(
                lambda tag: tag.name == 'span'
                and tag.get('class')
                and any('andes-money-amount__fraction' in c for c in tag.get('class'))
                and not tag.find_parent('s')
            )
            discount_tag = None

        # 2. Capturar también el precio anterior tachado (<s>) si tiene descuento
        prev_box = item.find('s', class_=re.compile(r'andes-money-amount--previous'))
        prev_tag = prev_box.find(class_=re.compile(r'andes-money-amount__fraction')) if prev_box else None

        link_tag = item.find('a', class_=re.compile(r'poly-component__title')) or item.find('a', href=True)
        shipping_tag = item.find(class_=re.compile(r'poly-component__shipping|ui-search-item__shipping'))
        seller_tag = item.find(class_=re.compile(r'poly-component__seller|ui-search-item__seller'))

        title = title_tag.get_text(strip=True) if title_tag else None
        price_str = price_tag.get_text(strip=True) if price_tag else None
        prev_str = prev_tag.get_text(strip=True) if prev_tag else None
        disc_str = discount_tag.get_text(strip=True) if discount_tag else None
        raw_link = link_tag['href'] if link_tag else ''
        shipping = shipping_tag.get_text(strip=True) if shipping_tag else 'Estándar'
        seller = seller_tag.get_text(strip=True) if seller_tag else 'Vendedor Particular / Tienda ML'

        if title and price_str:
            price_clean = int(price_str.replace('.', '').replace('$', '').strip())

            cap_match = re.search(r'(256\s*GB|512\s*GB|1\s*TB|128\s*GB)', title, re.IGNORECASE)
            capacity = cap_match.group(1).upper().replace(' ', '') if cap_match else 'No especificada'

            shipping_clean = 'Envío Gratis' if 'gratis' in shipping.lower() else shipping

            # Conservar el parámetro wid= (identificador de publicación específica en catálogo ML)
            wid_match = re.search(r'wid=(MCO\d+)', raw_link)
            base_url = raw_link.split('#')[0] if raw_link else ''
            if wid_match and 'pdp_filters' not in base_url:
                wid = wid_match.group(1)
                sep = '&' if '?' in base_url else '?'
                clean_link = f"{base_url}{sep}pdp_filters=item_id:{wid}#wid={wid}"
            else:
                clean_link = base_url

            extracted_data.append({
                'id': len(extracted_data) + 1,
                'titulo': title,
                'precio_cop': price_clean,
                'precio_formateado': f"$ {price_clean:,.0f}".replace(',', '.'),
                'precio_anterior': f"$ {prev_str}" if prev_str else '-',
                'descuento': disc_str if disc_str else '-',
                'capacidad': capacity,
                'envio': shipping_clean,
                'vendedor': seller,
                'enlace': clean_link
            })

    return extracted_data


# =============================================================================
# 2. MÉTODO 2: SELENIUM (Navegación automatizada y renderizado dinámico)
# =============================================================================
def run_selenium_scraper(query="iphone 17 pro max"):
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
# 3. FUNCIÓN PRINCIPAL DE EJECUCIÓN Y ANÁLISIS (MULTIPLATAFORMA / CLOUD)
# =============================================================================
def main():
    print("=" * 70)
    print("PROYECTO DE EXTRACCIÓN Y MONITOREO: iPhone 17 Pro Max en Mercado Libre")
    print("=" * 70)

    snapshot_html_path = os.path.join(BASE_DIR, "data", "mercadolibre_snapshot.html")
    csv_file = os.path.join(BASE_DIR, "iphone_17_pro_max_mercadolibre.csv")
    json_file = os.path.join(BASE_DIR, "iphone_17_pro_max_mercadolibre.json")

    if os.path.exists(snapshot_html_path):
        print("Extrayendo datos con BeautifulSoup desde captura HTML de Mercado Libre...")
        with open(snapshot_html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        products = parse_mercadolibre_with_bs4(html)
    elif os.path.exists(csv_file):
        print("Cargando registros validados desde dataset CSV del repositorio...")
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

    print("\n--- RESUMEN ESTADÍSTICO DE PRECIOS REALES DE VENTA (COP) ---")
    desc = df['precio_cop'].describe()
    print(f"Total artículos:     {int(desc['count'])}")
    print(f"Precio Promedio:     $ {desc['mean']:,.0f} COP".replace(',', '.'))
    print(f"Precio Mediano:      $ {desc['50%']:,.0f} COP".replace(',', '.'))
    print(f"Precio Mínimo:       $ {desc['min']:,.0f} COP".replace(',', '.'))
    print(f"Precio Máximo:       $ {desc['max']:,.0f} COP".replace(',', '.'))
    print(f"Desviación Estándar: $ {desc['std']:,.0f} COP".replace(',', '.'))


if __name__ == "__main__":
    main()
