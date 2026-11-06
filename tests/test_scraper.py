"""
=============================================================================
SUITE DE PRUEBAS AUTOMATIZADAS (CI/CD QUALITY GATE)
Proyecto: Monitoreo y Extracción de Datos - iPhone 17 Pro Max en Mercado Libre
Unidad 2: Optimizando la productividad en el mundo del software (DevOps & Git)
=============================================================================
"""

import os
import json
import unittest
import pandas as pd
from bs4 import BeautifulSoup
from scraper_mercadolibre import parse_mercadolibre_with_bs4


class TestMercadoLibreScraperPipeline(unittest.TestCase):
    """
    Pruebas unitarias y de integración para validar la funcionalidad del
    web scraping, la limpieza de datos y la integridad de los artefactos exportados.
    """

    @classmethod
    def setUpClass(cls):
        """Configuración inicial e inyección de HTML de prueba (Mock DOM de Mercado Libre)."""
        cls.sample_html = """
        <html>
            <body>
                <ol class="ui-search-layout">
                    <li class="ui-search-layout__item">
                        <div class="poly-card">
                            <h2 class="poly-component__title">Apple iPhone 17 Pro Max (256 GB) - Naranja cósmico - Distribuidor Autorizado</h2>
                            <span class="andes-money-amount__fraction">6.999.000</span>
                            <span class="poly-component__shipping">Llega gratis mañana</span>
                            <span class="poly-component__seller">Por Apple Tienda Oficial</span>
                            <a href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-256-gb/p/MCO1055308620#polycard_client=search">Ver producto</a>
                        </div>
                    </li>
                    <li class="ui-search-layout__item">
                        <div class="poly-card">
                            <h2 class="poly-component__title">Apple iPhone 17 Pro Max (512 GB) - Azul profundo</h2>
                            <span class="andes-money-amount__fraction">9.999.000</span>
                            <span class="poly-component__shipping">Envío gratis</span>
                            <a href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-512-gb/p/MCO55308673#tracking=123">Ver producto</a>
                        </div>
                    </li>
                    <li class="ui-search-layout__item">
                        <div class="poly-card">
                            <h2 class="poly-component__title">Apple iPhone 17 Pro Max (1 TB) - Color plata</h2>
                            <span class="andes-money-amount__fraction">5.990.098</span>
                            <span class="poly-component__shipping">Envío Estándar</span>
                            <a href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-1-tb/p/MCO55308695">Ver producto</a>
                        </div>
                    </li>
                </ol>
            </body>
        </html>
        """
        cls.parsed_items = parse_mercadolibre_with_bs4(cls.sample_html)

    def test_01_html_extraction_count(self):
        """Verifica que el parser BeautifulSoup extraiga exactamente los 3 ítems del DOM de prueba."""
        self.assertEqual(len(self.parsed_items), 3, "El número de productos extraídos debe ser 3.")

    def test_02_price_cleaning_and_numeric_type(self):
        """Valida que los precios en formato texto ('6.999.000') se conviertan a enteros (int) sin errores."""
        expected_prices = [6999000, 9999000, 5990098]
        for idx, item in enumerate(self.parsed_items):
            self.assertIsInstance(item['precio_cop'], int, "El precio debe ser de tipo entero.")
            self.assertEqual(item['precio_cop'], expected_prices[idx])
            self.assertGreater(item['precio_cop'], 1000000, "El precio en COP debe ser mayor a $1.000.000.")

    def test_03_storage_capacity_normalization(self):
        """Comprueba la detección mediante expresiones regulares de la capacidad (256GB, 512GB, 1TB)."""
        capacities = [item['capacidad'] for item in self.parsed_items]
        self.assertEqual(capacities, ['256GB', '512GB', '1TB'])

    def test_04_shipping_and_url_sanitization(self):
        """Verifica la normalización del envío gratis y la limpieza de fragmentos (#) en los enlaces."""
        self.assertEqual(self.parsed_items[0]['envio'], 'Envío Gratis')
        self.assertEqual(self.parsed_items[2]['envio'], 'Envío Estándar')
        for item in self.parsed_items:
            self.assertNotIn('#', item['enlace'], "La URL limpia no debe contener fragmentos de tracking (#).")
            self.assertTrue(item['enlace'].startswith('https://'), "El enlace debe utilizar protocolo seguro HTTPS.")

    def test_05_production_csv_dataset_integrity(self):
        """Audita la integridad del dataset de producción CSV (48 artículos de iPhone 17 Pro Max)."""
        csv_path = "iphone_17_pro_max_mercadolibre.csv"
        self.assertTrue(os.path.exists(csv_path), f"El archivo {csv_path} debe existir.")
        df = pd.read_csv(csv_path)
        self.assertGreaterEqual(len(df), 40, "El dataset debe contener al menos 40 registros válidos.")
        self.assertEqual(len(df), 48, "El dataset de producción debe contar con los 48 registros extraídos.")
        required_cols = {'id', 'titulo', 'precio_cop', 'precio_formateado', 'capacidad', 'envio', 'vendedor', 'enlace'}
        self.assertTrue(required_cols.issubset(set(df.columns)), "Faltan columnas obligatorias en el CSV.")
        self.assertEqual(df['precio_cop'].isnull().sum(), 0, "No deben existir precios nulos.")

    def test_06_production_json_dataset_integrity(self):
        """Audita la validez sintáctica y estructural del archivo JSON exportado."""
        json_path = "iphone_17_pro_max_mercadolibre.json"
        self.assertTrue(os.path.exists(json_path), f"El archivo {json_path} debe existir.")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 48)
        self.assertIn('iPhone 17 Pro Max', data[0]['titulo'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
