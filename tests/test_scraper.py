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
from scraper_mercadolibre import parse_mercadolibre_with_bs4


class TestMercadoLibreScraperPipeline(unittest.TestCase):
    """
    Pruebas unitarias y de integración para validar la funcionalidad del
    web scraping, la diferenciación entre precio tachado y precio actual,
    y la integridad de los artefactos exportados.
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
                            <a class="poly-component__title" href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-256-gb/p/MCO1055308620#wid=MCO3114162628">Apple iPhone 17 Pro Max (256 GB) - Naranja cósmico - Distribuidor Autorizado</a>
                            <div class="poly-component__price">
                                <s class="andes-money-amount andes-money-amount--previous">
                                    <span class="andes-money-amount__fraction">6.999.000</span>
                                </s>
                                <div class="poly-price__current">
                                    <span class="andes-money-amount__fraction">5.685.686</span>
                                    <span class="poly-price__discount">18% OFF</span>
                                </div>
                            </div>
                            <span class="poly-component__shipping">Llega gratis mañana</span>
                            <span class="poly-component__seller">Apple Tienda Oficial</span>
                        </div>
                    </li>
                    <li class="ui-search-layout__item">
                        <div class="poly-card">
                            <a class="poly-component__title" href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-512-gb/p/MCO55308673">Apple iPhone 17 Pro Max (512 GB) - Azul profundo</a>
                            <div class="poly-price__current">
                                <span class="andes-money-amount__fraction">5.699.900</span>
                            </div>
                            <span class="poly-component__shipping">Envío gratis</span>
                        </div>
                    </li>
                    <li class="ui-search-layout__item">
                        <div class="poly-card">
                            <a class="poly-component__title" href="https://www.mercadolibre.com.co/apple-iphone-17-pro-max-1-tb/p/MCO55308695">Apple iPhone 17 Pro Max (1 TB) - Color plata</a>
                            <div class="poly-price__current">
                                <span class="andes-money-amount__fraction">5.990.098</span>
                            </div>
                            <span class="poly-component__shipping">Envío Estándar</span>
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

    def test_02_current_price_vs_crossed_out_price(self):
        """Valida que se extraiga el precio actual de venta (5.685.686) y NO el precio anterior tachado (6.999.000)."""
        expected_prices = [5685686, 5699900, 5990098]
        for idx, item in enumerate(self.parsed_items):
            self.assertIsInstance(item['precio_cop'], int, "El precio debe ser de tipo entero.")
            self.assertEqual(item['precio_cop'], expected_prices[idx])
        self.assertEqual(self.parsed_items[0]['precio_anterior'], '$ 6.999.000')
        self.assertEqual(self.parsed_items[0]['descuento'], '18% OFF')

    def test_03_storage_capacity_normalization(self):
        """Comprueba la detección mediante expresiones regulares de la capacidad (256GB, 512GB, 1TB)."""
        capacities = [item['capacidad'] for item in self.parsed_items]
        self.assertEqual(capacities, ['256GB', '512GB', '1TB'])

    def test_04_shipping_and_wid_url_preservation(self):
        """Verifica la normalización del envío gratis y que se conserve el identificador de oferta wid= en la URL."""
        self.assertEqual(self.parsed_items[0]['envio'], 'Envío Gratis')
        self.assertEqual(self.parsed_items[2]['envio'], 'Envío Estándar')
        self.assertIn('MCO3114162628', self.parsed_items[0]['enlace'])

    def test_05_production_csv_dataset_integrity(self):
        """Audita la integridad del dataset de producción CSV (48 artículos de iPhone 17 Pro Max)."""
        csv_path = "iphone_17_pro_max_mercadolibre.csv"
        self.assertTrue(os.path.exists(csv_path), f"El archivo {csv_path} debe existir.")
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 48, "El dataset de producción debe contar con los 48 registros extraídos.")
        self.assertEqual(int(df.iloc[0]['precio_cop']), 5685686, "El primer producto debe tener el precio actual real $5.685.686.")
        self.assertEqual(df['precio_cop'].isnull().sum(), 0, "No deben existir precios nulos.")

    def test_06_production_json_dataset_integrity(self):
        """Audita la validez sintáctica y estructural del archivo JSON exportado."""
        json_path = "iphone_17_pro_max_mercadolibre.json"
        self.assertTrue(os.path.exists(json_path), f"El archivo {json_path} debe existir.")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 48)
        self.assertEqual(data[0]['precio_cop'], 5685686)


if __name__ == '__main__':
    unittest.main(verbosity=2)
