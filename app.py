"""
=============================================================================
APLICACIÓN WEB PYTHON WSGI Y API REST DE MONITOREO (EA3)
Proyecto: Monitoreo de Precios iPhone 17 Pro Max en Mercado Libre Colombia
Unidad 3: Optimización de Procesos de Desarrollo con GitHub Actions y Cloud
=============================================================================
Aplicación web ligera compatible con el estándar WSGI (PEP 3333) y configurable
mediante variables de entorno (.env.example). Expone:
  - GET /                       : Interfaz web interactiva con gráficas y filtros
  - GET /api/health             : Estado de salud del servicio y variables de entorno
  - GET /api/metrics            : Estadísticas descriptivas y distribución por capacidad
  - GET /api/products           : Catálogo filtrable (?capacidad=256GB&descuento=true&q=...&sort=asc)
  - GET /api/iphone17_data.json : Payload completo compatible con despliegue estático
=============================================================================
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Callable, Iterable, Tuple
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

import pandas as pd

from deploy_dashboard import compute_market_metrics, get_runtime_config, render_web_html


def _json_response(
    start_response: Callable, payload: dict, status: str = "200 OK"
) -> Iterable[bytes]:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Access-Control-Allow-Origin", "*"),
        ("X-Service-Version", os.getenv("APP_VERSION", "3.0.0")),
    ]
    start_response(status, headers)
    return [body]


def _html_response(
    start_response: Callable, html: str, status: str = "200 OK"
) -> Iterable[bytes]:
    body = html.encode("utf-8")
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("X-Service-Version", os.getenv("APP_VERSION", "3.0.0")),
    ]
    start_response(status, headers)
    return [body]


def load_catalog_dataframe() -> pd.DataFrame:
    """Carga el catálogo validado de Mercado Libre desde DATA_PATH."""
    cfg = get_runtime_config()
    return pd.read_csv(cfg["data_path"])


def filter_products(df: pd.DataFrame, query_params: dict) -> pd.DataFrame:
    """Aplica filtros dinámicos de búsqueda, capacidad, descuento, rango y orden."""
    filtered = df.copy()

    capacidad = query_params.get("capacidad", [None])[0]
    if capacidad and capacidad.upper() != "ALL":
        filtered = filtered[
            filtered["capacidad"].astype(str).str.upper() == capacidad.upper()
        ]

    descuento = query_params.get("descuento", [None])[0]
    if descuento and descuento.lower() in ("true", "1", "yes", "si"):
        filtered = filtered[
            filtered["descuento"].astype(str).str.contains("OFF", case=False, na=False)
        ]

    q = query_params.get("q", [None])[0]
    if q:
        filtered = filtered[
            filtered["titulo"].astype(str).str.contains(q, case=False, na=False)
        ]

    min_price = query_params.get("min_price", [None])[0]
    if min_price and min_price.isdigit():
        filtered = filtered[filtered["precio_cop"] >= int(min_price)]

    max_price = query_params.get("max_price", [None])[0]
    if max_price and max_price.isdigit():
        filtered = filtered[filtered["precio_cop"] <= int(max_price)]

    sort_order = query_params.get("sort", ["id"])[0].lower()
    if sort_order in ("asc", "price-asc"):
        filtered = filtered.sort_values(by="precio_cop", ascending=True)
    elif sort_order in ("desc", "price-desc"):
        filtered = filtered.sort_values(by="precio_cop", ascending=False)

    return filtered


def application(environ: dict, start_response: Callable) -> Iterable[bytes]:
    """Punto de entrada WSGI estándar compatible con servidores locales y en la nube."""
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    query_params = parse_qs(environ.get("QUERY_STRING", ""))

    if method != "GET":
        return _json_response(
            start_response,
            {"error": "Method Not Allowed", "allowed": ["GET"]},
            status="405 Method Not Allowed",
        )

    cfg = get_runtime_config()
    df = load_catalog_dataframe()
    metrics = compute_market_metrics(df)
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if path in ("/", "/index.html"):
        html = render_web_html(df.to_dict(orient="records"), metrics, cfg, now_utc)
        return _html_response(start_response, html)

    if path in ("/api/health", "/api/health.json"):
        return _json_response(
            start_response,
            {
                "status": "ok",
                "service": "mercadolibre-iphone17pm-web",
                "version": cfg["app_version"],
                "environment": cfg["app_env"],
                "deploy_target": cfg["deploy_target"],
                "records_loaded": int(len(df)),
                "timestamp_utc": now_utc,
            },
        )

    if path == "/api/metrics":
        return _json_response(
            start_response,
            {
                "version": cfg["app_version"],
                "environment": cfg["app_env"],
                "total_records": int(len(df)),
                "currency": "COP",
                "metrics": metrics,
            },
        )

    if path == "/api/products":
        filtered_df = filter_products(df, query_params)
        return _json_response(
            start_response,
            {
                "total_matched": int(len(filtered_df)),
                "filters_applied": {k: v[0] for k, v in query_params.items()},
                "data": filtered_df.to_dict(orient="records"),
            },
        )

    if path == "/api/iphone17_data.json":
        return _json_response(
            start_response,
            {
                "metadata": {
                    "project": "Mercado Libre Price Intelligence - iPhone 17 Pro Max",
                    "version": cfg["app_version"],
                    "environment": cfg["app_env"],
                    "total_records": int(len(df)),
                    "currency": "COP",
                    "metrics": metrics,
                },
                "data": df.to_dict(orient="records"),
            },
        )

    return _json_response(
        start_response,
        {
            "error": "Not Found",
            "path": path,
            "available_endpoints": [
                "/",
                "/api/health",
                "/api/metrics",
                "/api/products",
                "/api/iphone17_data.json",
            ],
        },
        status="404 Not Found",
    )


def create_server(host: str | None = None, port: int | None = None) -> Tuple[object, int]:
    """Instancia el servidor HTTP WSGI leyendo HOST y PORT de las variables de entorno."""
    bind_host = host or os.getenv("HOST", "0.0.0.0")
    bind_port = port if port is not None else int(os.getenv("PORT", "8000"))
    httpd = make_server(bind_host, bind_port, application)
    return httpd, httpd.server_address[1]


def main() -> None:
    cfg = get_runtime_config()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    httpd, actual_port = create_server(host, port)
    print(
        f"[WEB APP] Servidor WSGI iniciado en http://{host}:{actual_port} "
        f"(env={cfg['app_env']}, version=v{cfg['app_version']})"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[WEB APP] Servidor detenido correctamente.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
