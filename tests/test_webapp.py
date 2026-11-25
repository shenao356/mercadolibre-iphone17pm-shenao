"""
=============================================================================
SUITE DE PRUEBAS DE INTEGRACIÓN PARA LA APLICACIÓN WEB Y DESPLIEGUE CD (EA3)
Proyecto: Monitoreo iPhone 17 Pro Max en Mercado Libre Colombia
Unidad 3: Optimización de Procesos de Desarrollo con GitHub Actions
=============================================================================
Valida mediante pruebas automatizadas:
  1. Disponibilidad HTTP 200 de la aplicación web WSGI (GET /).
  2. Respuesta y esquema del endpoint de salud (/api/health).
  3. Exactitud estadística del endpoint de métricas (/api/metrics).
  4. Filtrado dinámico por capacidad, descuento y ordenamiento (/api/products).
  5. Manejo correcto de rutas inexistentes (HTTP 404).
  6. Generación de artefactos de despliegue continuo (docs/index.html, JSONs, .nojekyll).
  7. Inyección de variables de entorno (APP_ENV, APP_VERSION, BUILD_COMMIT_SHA).
=============================================================================
"""

import json
import os
import tempfile
import threading
import unittest

import requests

from app import create_server
from deploy_dashboard import build_deployment_artifacts


class TestWebAppAndCloudDeployment(unittest.TestCase):
    """Pruebas de integración HTTP sobre el servidor WSGI y el generador CD."""

    @classmethod
    def setUpClass(cls):
        """Levanta una instancia real del servidor web WSGI en un puerto efímero."""
        cls.httpd, cls.port = create_server(host="127.0.0.1", port=0)
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        """Detiene limpiamente el servidor WSGI al finalizar la suite."""
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def test_01_homepage_renders_dashboard_html(self):
        """Verifica que la ruta raíz '/' retorne HTTP 200 con la interfaz web interactiva."""
        resp = requests.get(f"{self.base_url}/", timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers.get("Content-Type", ""))
        self.assertIn("iPhone 17 Pro Max", resp.text)
        self.assertIn("capacityChart", resp.text)
        self.assertIn("histogramChart", resp.text)

    def test_02_api_health_endpoint_ok(self):
        """Valida el endpoint de monitoreo '/api/health' para verificación en la nube."""
        resp = requests.get(f"{self.base_url}/api/health", timeout=5)
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "mercadolibre-iphone17pm-web")
        self.assertEqual(payload["records_loaded"], 48)

    def test_03_api_metrics_returns_exact_statistics(self):
        """Comprueba que '/api/metrics' retorne los KPIs estadísticos exactos en COP."""
        resp = requests.get(f"{self.base_url}/api/metrics", timeout=5)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total_records"], 48)
        self.assertEqual(body["currency"], "COP")
        self.assertEqual(body["metrics"]["min_price"], 2667777)
        self.assertEqual(body["metrics"]["max_price"], 7990000)
        self.assertGreater(body["metrics"]["discount_count"], 0)

    def test_04_api_products_filter_by_capacity(self):
        """Valida el filtrado dinámico por capacidad en '/api/products?capacidad=512GB'."""
        resp = requests.get(f"{self.base_url}/api/products?capacidad=512GB", timeout=5)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total_matched"], 8)
        for item in body["data"]:
            self.assertEqual(item["capacidad"], "512GB")

    def test_05_api_products_filter_discounts_and_sort(self):
        """Valida filtrado de productos con descuento activo y orden ascendente de precio."""
        resp = requests.get(
            f"{self.base_url}/api/products?descuento=true&sort=asc", timeout=5
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertGreaterEqual(body["total_matched"], 3)
        prices = [item["precio_cop"] for item in body["data"]]
        self.assertEqual(prices, sorted(prices))
        for item in body["data"]:
            self.assertIn("OFF", str(item["descuento"]).upper())

    def test_06_unknown_route_returns_404_json(self):
        """Comprueba que rutas inexistentes respondan HTTP 404 en formato JSON controlado."""
        resp = requests.get(f"{self.base_url}/ruta-inexistente", timeout=5)
        self.assertEqual(resp.status_code, 404)
        body = resp.json()
        self.assertEqual(body["error"], "Not Found")
        self.assertIn("/api/health", body["available_endpoints"])

    def test_07_static_cloud_build_generates_all_artifacts(self):
        """Audita que deploy_dashboard.py genere el bundle completo de GitHub Pages con variables de entorno."""
        prev_env = os.environ.get("APP_ENV")
        prev_sha = os.environ.get("BUILD_COMMIT_SHA")
        os.environ["APP_ENV"] = "staging"
        os.environ["BUILD_COMMIT_SHA"] = "abc1234567"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = build_deployment_artifacts(output_dir=tmpdir)
                self.assertTrue(os.path.exists(result["index_html"]))
                self.assertTrue(os.path.exists(result["data_json"]))
                self.assertTrue(os.path.exists(result["health_json"]))
                self.assertTrue(os.path.exists(os.path.join(tmpdir, ".nojekyll")))

                with open(result["health_json"], "r", encoding="utf-8") as f:
                    health = json.load(f)
                self.assertEqual(health["status"], "ok")
                self.assertEqual(health["environment"], "staging")
                self.assertEqual(health["build_commit_sha"], "abc1234567")
        finally:
            if prev_env is None:
                os.environ.pop("APP_ENV", None)
            else:
                os.environ["APP_ENV"] = prev_env
            if prev_sha is None:
                os.environ.pop("BUILD_COMMIT_SHA", None)
            else:
                os.environ["BUILD_COMMIT_SHA"] = prev_sha

    def test_08_production_docs_bundle_integrity(self):
        """Audita que los artefactos de producción en 'docs/' estén generados y sin corrupción."""
        self.assertTrue(os.path.exists("docs/index.html"))
        self.assertTrue(os.path.exists("docs/api/iphone17_data.json"))
        self.assertTrue(os.path.exists("docs/api/health.json"))
        with open("docs/api/iphone17_data.json", "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.assertEqual(payload["metadata"]["total_records"], 48)
        self.assertEqual(len(payload["data"]), 48)


if __name__ == "__main__":
    unittest.main(verbosity=2)
