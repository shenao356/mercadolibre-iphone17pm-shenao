"""
=============================================================================
CONTINUOUS DEPLOYMENT (CD) GENERATOR - APLICACIÓN WEB & API DE PRODUCCIÓN
Proyecto: Monitoreo iPhone 17 Pro Max en Mercado Libre Colombia
Unidad 3 (EA3): Optimización de Procesos de Desarrollo con GitHub Actions
=============================================================================
Genera los artefactos estáticos listos para alojamiento en la nube (GitHub Pages):
  - <OUTPUT_DIR>/index.html              : Aplicación Web SPA interactiva con gráficas
  - <OUTPUT_DIR>/api/iphone17_data.json  : Endpoint API JSON con métricas y catálogo
  - <OUTPUT_DIR>/api/health.json         : Endpoint estático de salud y trazabilidad CI/CD
  - <OUTPUT_DIR>/.nojekyll               : Desactiva el procesamiento Jekyll en GitHub Pages

Variables de entorno soportadas:
  APP_ENV, APP_VERSION, DATA_PATH, OUTPUT_DIR, DEPLOY_TARGET,
  BUILD_COMMIT_SHA, BUILD_RUN_NUMBER
=============================================================================
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Any, Dict

import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fmt_cop(val: float) -> str:
    """Formatea un valor numérico a pesos colombianos (COP) con separador de miles."""
    return f"$ {val:,.0f}".replace(",", ".")


def get_runtime_config() -> Dict[str, str]:
    """Lee la configuración de entorno inyectada por GitHub Actions o archivo local."""
    return {
        "app_env": os.getenv("APP_ENV", "production"),
        "app_version": os.getenv("APP_VERSION", "3.0.0"),
        "data_path": os.getenv(
            "DATA_PATH", os.path.join(BASE_DIR, "iphone_17_pro_max_mercadolibre.csv")
        ),
        "output_dir": os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "docs")),
        "deploy_target": os.getenv("DEPLOY_TARGET", "GitHub Pages"),
        "build_commit_sha": os.getenv("BUILD_COMMIT_SHA", "local-build")[:10],
        "build_run_number": os.getenv("BUILD_RUN_NUMBER", "1"),
    }


def compute_market_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estadísticas descriptivas, distribución por capacidad y rangos de precio."""
    mean_val = float(df["precio_cop"].mean())
    median_val = float(df["precio_cop"].median())
    min_val = int(df["precio_cop"].min())
    max_val = int(df["precio_cop"].max())
    std_val = float(df["precio_cop"].std())
    cv_val = round((std_val / mean_val) * 100.0, 2) if mean_val else 0.0

    # Conteo de artículos con descuento activo
    has_discount = df["descuento"].astype(str).str.contains("OFF", case=False, na=False)
    discount_count = int(has_discount.sum())

    # Desglose por capacidad de almacenamiento
    cap_order = ["256GB", "512GB", "1TB", "No especificada"]
    capacity_summary = []
    for cap in cap_order:
        sub = df[df["capacidad"] == cap]
        if len(sub) > 0:
            capacity_summary.append(
                {
                    "capacidad": cap,
                    "cantidad": int(len(sub)),
                    "porcentaje": round((len(sub) / len(df)) * 100.0, 1),
                    "precio_promedio": round(float(sub["precio_cop"].mean()), 2),
                    "precio_minimo": int(sub["precio_cop"].min()),
                    "precio_maximo": int(sub["precio_cop"].max()),
                }
            )

    # Rangos para histograma de distribución de precios (en millones COP)
    bins = [0, 3_500_000, 4_500_000, 5_500_000, 6_500_000, 10_000_000]
    labels = ["< 3.5M", "3.5M - 4.5M", "4.5M - 5.5M", "5.5M - 6.5M", "> 6.5M"]
    binned = pd.cut(df["precio_cop"], bins=bins, labels=labels, right=True)
    hist_counts = [int((binned == lbl).sum()) for lbl in labels]

    return {
        "mean_price": round(mean_val, 2),
        "median_price": round(median_val, 2),
        "min_price": min_val,
        "max_price": max_val,
        "std_price": round(std_val, 2),
        "range_price": max_val - min_val,
        "cv_percent": cv_val,
        "discount_count": discount_count,
        "capacity_summary": capacity_summary,
        "price_distribution": {"labels": labels, "counts": hist_counts},
    }


def render_web_html(
    records: list[dict], metrics: Dict[str, Any], cfg: Dict[str, str], built_at: str
) -> str:
    """Construye la aplicación web interactiva SPA con gráficas Chart.js y filtros en vivo."""
    mean_str = fmt_cop(metrics["mean_price"])
    median_str = fmt_cop(metrics["median_price"])
    min_str = fmt_cop(metrics["min_price"])
    max_str = fmt_cop(metrics["max_price"])
    std_str = fmt_cop(metrics["std_price"])

    cap_map = {c["capacidad"]: c for c in metrics["capacity_summary"]}
    c256 = cap_map.get("256GB", {"cantidad": 0, "precio_promedio": 0})
    c512 = cap_map.get("512GB", {"cantidad": 0, "precio_promedio": 0})
    c1tb = cap_map.get("1TB", {"cantidad": 0, "precio_promedio": 0})

    # Datos serializados para gráficas interactivas en el navegador
    cap_labels_json = json.dumps([c["capacidad"] for c in metrics["capacity_summary"]], ensure_ascii=False)
    cap_means_json = json.dumps([round(c["precio_promedio"] / 1_000_000, 2) for c in metrics["capacity_summary"]])
    cap_counts_json = json.dumps([c["cantidad"] for c in metrics["capacity_summary"]])
    hist_labels_json = json.dumps(metrics["price_distribution"]["labels"], ensure_ascii=False)
    hist_counts_json = json.dumps(metrics["price_distribution"]["counts"])

    rows_html = ""
    for r in records:
        cap_val = str(r["capacidad"])
        cap_class = (
            "cap-256"
            if "256" in cap_val
            else (
                "cap-512"
                if "512" in cap_val
                else ("cap-1tb" if "1TB" in cap_val else "cap-other")
            )
        )

        prev_price = str(r.get("precio_anterior", "-"))
        disc = str(r.get("descuento", "-"))
        has_disc_attr = "true" if ("OFF" in disc.upper()) else "false"

        if prev_price != "-" and prev_price != "nan":
            price_cell_html = f"""
                <div class="old-price">Antes: <s>{prev_price}</s></div>
                <div class="curr-price">{r['precio_formateado']} <span class="disc-badge">{disc}</span></div>
            """
        else:
            price_cell_html = f"""<div class="curr-price">{r['precio_formateado']}</div>"""

        rows_html += f"""
        <tr data-capacity="{cap_val}" data-discount="{has_disc_attr}" data-price="{int(r['precio_cop'])}" data-id="{int(r['id'])}">
            <td class="col-id">#{r['id']}</td>
            <td class="col-title">{r['titulo']}</td>
            <td class="col-price">{price_cell_html}</td>
            <td><span class="badge {cap_class}">{cap_val}</span></td>
            <td><span class="badge ship">{r['envio']}</span></td>
            <td><a class="btn-link" href="{r['enlace']}" target="_blank" rel="noopener">Abrir en ML &rarr;</a></td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor Web CI/CD | iPhone 17 Pro Max - Mercado Libre</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: #e2e8f0;
            color: #0f172a;
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }}
        header {{
            background-color: #0b192c;
            background-image: linear-gradient(135deg, #0b192c 0%, #1e3e62 100%);
            color: #ffffff;
            padding: 1.85rem 2.5rem;
            border-bottom: 5px solid #ffe600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
        }}
        .header-inner {{
            max-width: 1260px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}
        header h1 {{
            margin: 0;
            font-size: 1.65rem;
            color: #ffffff;
            letter-spacing: -0.3px;
        }}
        header p {{
            margin: 0.35rem 0 0;
            color: #cbd5e1;
            font-size: 0.94rem;
        }}
        .status-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            align-items: center;
        }}
        .status-pill {{
            background-color: #065f46;
            border: 2px solid #34d399;
            color: #ecfdf5;
            padding: 0.45rem 1rem;
            border-radius: 999px;
            font-size: 0.84rem;
            font-weight: 700;
        }}
        .env-pill {{
            background-color: #1e293b;
            border: 1px solid #64748b;
            color: #fde047;
            padding: 0.45rem 0.9rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .container {{
            max-width: 1260px;
            margin: 1.8rem auto;
            padding: 0 1.5rem;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.2rem;
            margin-bottom: 1.8rem;
        }}
        .kpi-card {{
            background-color: #ffffff;
            padding: 1.35rem 1.45rem;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            border-top: 5px solid #1e3e62;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.08);
        }}
        .kpi-card h3 {{
            margin: 0;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #334155;
            font-weight: 700;
        }}
        .kpi-card .value {{
            font-size: 1.55rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.4rem;
        }}
        .kpi-card .sub {{
            font-size: 0.8rem;
            color: #475569;
            margin-top: 0.25rem;
            font-weight: 500;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.2rem;
            margin-bottom: 1.8rem;
        }}
        .cap-box {{
            background-color: #1e293b;
            color: #f8fafc;
            padding: 1.15rem 1.4rem;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.12);
        }}
        .cap-box .cap-label {{ font-size: 1.02rem; font-weight: 700; color: #ffe600; }}
        .cap-box .cap-desc {{ font-size: 0.84rem; color: #cbd5e1; }}
        .cap-box .cap-count {{
            font-size: 1.45rem;
            font-weight: 800;
            background-color: #334155;
            color: #ffffff;
            padding: 0.3rem 0.85rem;
            border-radius: 8px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 1.25rem;
            margin-bottom: 1.8rem;
        }}
        .chart-card {{
            background-color: #ffffff;
            padding: 1.4rem 1.5rem;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 8px rgba(15, 23, 42, 0.08);
        }}
        .chart-card h2 {{
            margin: 0 0 1rem;
            font-size: 1.05rem;
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.6rem;
        }}
        .chart-wrap {{
            position: relative;
            height: 255px;
        }}
        .card-panel {{
            background-color: #ffffff;
            padding: 1.65rem;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
            margin-bottom: 1.8rem;
            overflow-x: auto;
        }}
        .panel-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            gap: 0.85rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1rem;
        }}
        .panel-header h2 {{
            margin: 0;
            font-size: 1.2rem;
            color: #0f172a;
        }}
        .controls-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            align-items: center;
        }}
        .search-input, .select-input {{
            padding: 0.52rem 0.9rem;
            border: 2px solid #94a3b8;
            border-radius: 8px;
            font-size: 0.88rem;
            color: #0f172a;
            background-color: #f8fafc;
            font-weight: 500;
        }}
        .search-input {{ min-width: 240px; }}
        .search-input:focus, .select-input:focus {{
            outline: none;
            border-color: #1e3e62;
            background-color: #ffffff;
        }}
        .toggle-label {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.86rem;
            font-weight: 700;
            color: #166534;
            background-color: #dcfce7;
            border: 1px solid #86efac;
            padding: 0.45rem 0.75rem;
            border-radius: 8px;
            cursor: pointer;
        }}
        .results-counter {{
            font-size: 0.85rem;
            color: #475569;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th {{
            background-color: #0f172a;
            color: #ffffff;
            padding: 0.9rem 0.95rem;
            text-align: left;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.4px;
        }}
        td {{
            padding: 0.85rem 0.95rem;
            text-align: left;
            border-bottom: 1px solid #cbd5e1;
            color: #1e293b;
        }}
        tbody tr:nth-child(even) {{ background-color: #f1f5f9; }}
        tbody tr:nth-child(odd) {{ background-color: #ffffff; }}
        tbody tr:hover {{ background-color: #dbeafe; }}
        .col-id {{ font-weight: 700; color: #475569; width: 58px; }}
        .col-title {{ font-weight: 600; color: #0f172a; }}
        .col-price {{ white-space: nowrap; }}
        .old-price {{ font-size: 0.76rem; color: #64748b; font-weight: 500; margin-bottom: 2px; }}
        .curr-price {{ font-weight: 800; color: #047857; font-size: 1rem; }}
        .disc-badge {{
            background-color: #dcfce7;
            color: #166534;
            border: 1px solid #86efac;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-left: 4px;
        }}
        .badge {{
            display: inline-block;
            padding: 0.28rem 0.62rem;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            white-space: nowrap;
        }}
        .cap-256 {{ background-color: #1e3a8a; color: #ffffff; }}
        .cap-512 {{ background-color: #581c87; color: #ffffff; }}
        .cap-1tb {{ background-color: #9a3412; color: #ffffff; }}
        .cap-other {{ background-color: #475569; color: #ffffff; }}
        .badge.ship {{ background-color: #065f46; color: #ffffff; }}
        .btn-link {{
            display: inline-block;
            background-color: #1e3e62;
            color: #ffffff;
            padding: 0.38rem 0.78rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.8rem;
            white-space: nowrap;
        }}
        .btn-link:hover {{ background-color: #0b192c; }}
        .devops-bar {{
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #0284c7;
            border-radius: 8px;
            padding: 1rem 1.35rem;
            margin-bottom: 1.8rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.85rem;
        }}
        .devops-bar code {{
            background-color: #e2e8f0;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-weight: 700;
            color: #0f172a;
        }}
        footer {{
            background-color: #0f172a;
            color: #e2e8f0;
            text-align: center;
            padding: 1.7rem;
            margin-top: 2.5rem;
            font-size: 0.88rem;
        }}
        footer a {{ color: #ffe600; text-decoration: none; font-weight: 700; }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <div>
                <h1>📱 Monitor Web CI/CD: Apple iPhone 17 Pro Max en Mercado Libre</h1>
                <p>IU Digital de Antioquia &bull; Programación para Análisis de Datos &bull; Evidencia de Aprendizaje 3 (GitHub Actions &amp; Cloud Deployment)</p>
            </div>
            <div class="status-group">
                <span class="status-pill">&#10004; CI/CD Activo &bull; {len(records)} Artículos</span>
                <span class="env-pill">v{cfg['app_version']} &bull; {cfg['app_env'].upper()} &bull; {cfg['deploy_target']}</span>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="devops-bar">
            <div>
                <strong>Trazabilidad de Despliegue Continuo:</strong>
                Commit <code>{cfg['build_commit_sha']}</code> &bull;
                Build <code>#{cfg['build_run_number']}</code> &bull;
                Generado: <code>{built_at}</code>
            </div>
            <div>
                Endpoints activos:
                <a href="api/iphone17_data.json" target="_blank"><code>api/iphone17_data.json</code></a> &bull;
                <a href="api/health.json" target="_blank"><code>api/health.json</code></a>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Total Publicaciones</h3>
                <div class="value">{len(records)} Celulares</div>
                <div class="sub">{metrics['discount_count']} ofertas con descuento activo</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Promedio (Media)</h3>
                <div class="value">{mean_str}</div>
                <div class="sub">Desviación: {std_str} (CV {metrics['cv_percent']}%)</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Mediano (50%)</h3>
                <div class="value">{median_str}</div>
                <div class="sub">Punto medio real de venta</div>
            </div>
            <div class="kpi-card">
                <h3>Rango Mínimo / Máximo</h3>
                <div class="value" style="font-size: 1.15rem;">{min_str} / {max_str}</div>
                <div class="sub">Amplitud: {fmt_cop(metrics['range_price'])} COP</div>
            </div>
        </div>

        <div class="summary-grid">
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 256 GB</div>
                    <div class="cap-desc">Promedio: {fmt_cop(c256['precio_promedio'])} COP</div>
                </div>
                <div class="cap-count">{c256['cantidad']}</div>
            </div>
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 512 GB</div>
                    <div class="cap-desc">Promedio: {fmt_cop(c512['precio_promedio'])} COP</div>
                </div>
                <div class="cap-count">{c512['cantidad']}</div>
            </div>
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 1 TB</div>
                    <div class="cap-desc">Promedio: {fmt_cop(c1tb['precio_promedio'])} COP</div>
                </div>
                <div class="cap-count">{c1tb['cantidad']}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h2>Precio Promedio por Capacidad de Almacenamiento (Millones COP)</h2>
                <div class="chart-wrap">
                    <canvas id="capacityChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h2>Distribución de Ofertas por Rango de Precio (COP)</h2>
                <div class="chart-wrap">
                    <canvas id="histogramChart"></canvas>
                </div>
            </div>
        </div>

        <div class="card-panel">
            <div class="panel-header">
                <h2>Catálogo Interactivo Extraído ({len(records)} Registros Validados)</h2>
                <div class="controls-bar">
                    <input type="text" id="tableFilter" class="search-input" placeholder="🔍 Buscar título o palabra clave..." onkeyup="applyFilters()">
                    <select id="capFilter" class="select-input" onchange="applyFilters()">
                        <option value="ALL">Todas las capacidades</option>
                        <option value="256GB">256 GB</option>
                        <option value="512GB">512 GB</option>
                        <option value="1TB">1 TB</option>
                        <option value="No especificada">No especificada</option>
                    </select>
                    <select id="sortSelect" class="select-input" onchange="applyFilters()">
                        <option value="id">Orden original (#)</option>
                        <option value="price-asc">Precio: menor a mayor</option>
                        <option value="price-desc">Precio: mayor a menor</option>
                    </select>
                    <label class="toggle-label">
                        <input type="checkbox" id="discountOnly" onchange="applyFilters()"> Solo con descuento
                    </label>
                </div>
            </div>
            <div id="resultsCounter" class="results-counter">Mostrando {len(records)} de {len(records)} publicaciones</div>
            <table id="productsTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Título de la Publicación en Mercado Libre</th>
                        <th>Precio Actual / Descuento</th>
                        <th>Capacidad</th>
                        <th>Envío</th>
                        <th>Publicación</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <footer>
        Automatizado con <strong>GitHub Actions (CI/CD)</strong> y desplegado en <strong>{cfg['deploy_target']}</strong> &bull;
        Repositorio: <a href="https://github.com/shenao356/mercadolibre-iphone17pm-shenao" target="_blank">shenao356/mercadolibre-iphone17pm-shenao</a> &bull;
        API JSON: <a href="api/iphone17_data.json" target="_blank">api/iphone17_data.json</a> &bull;
        Health: <a href="api/health.json" target="_blank">api/health.json</a>
    </footer>

    <script>
        // Gráfica 1: Precio promedio por capacidad
        if (typeof Chart !== 'undefined') {{
            new Chart(document.getElementById('capacityChart'), {{
                type: 'bar',
                data: {{
                    labels: {cap_labels_json},
                    datasets: [{{
                        label: 'Precio Promedio (Millones COP)',
                        data: {cap_means_json},
                        backgroundColor: ['#1e3a8a', '#581c87', '#9a3412', '#475569'],
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Millones COP' }} }} }}
                }}
            }});

            // Gráfica 2: Distribución de frecuencias por rango de precio
            new Chart(document.getElementById('histogramChart'), {{
                type: 'bar',
                data: {{
                    labels: {hist_labels_json},
                    datasets: [{{
                        label: 'Publicaciones',
                        data: {hist_counts_json},
                        backgroundColor: '#0284c7',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 5 }}, title: {{ display: true, text: 'Cantidad de ofertas' }} }} }}
                }}
            }});
        }}

        // Filtrado y ordenamiento interactivo en tiempo real
        function applyFilters() {{
            const query = document.getElementById('tableFilter').value.toLowerCase();
            const cap = document.getElementById('capFilter').value;
            const onlyDisc = document.getElementById('discountOnly').checked;
            const sortBy = document.getElementById('sortSelect').value;

            const tbody = document.querySelector('#productsTable tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            rows.sort((a, b) => {{
                if (sortBy === 'price-asc') return Number(a.dataset.price) - Number(b.dataset.price);
                if (sortBy === 'price-desc') return Number(b.dataset.price) - Number(a.dataset.price);
                return Number(a.dataset.id) - Number(b.dataset.id);
            }});

            let visible = 0;
            rows.forEach(row => {{
                tbody.appendChild(row);
                const textMatch = row.innerText.toLowerCase().includes(query);
                const capMatch = (cap === 'ALL') || (row.dataset.capacity === cap);
                const discMatch = (!onlyDisc) || (row.dataset.discount === 'true');
                const show = textMatch && capMatch && discMatch;
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});

            document.getElementById('resultsCounter').innerText =
                `Mostrando ${{visible}} de ${{rows.length}} publicaciones`;
        }}
    </script>
</body>
</html>
"""


def build_deployment_artifacts(
    output_dir: str | None = None, data_path: str | None = None
) -> Dict[str, Any]:
    """Construye los artefactos web y JSON de producción para el despliegue en la nube."""
    cfg = get_runtime_config()
    if output_dir:
        cfg["output_dir"] = output_dir
    if data_path:
        cfg["data_path"] = data_path

    df = pd.read_csv(cfg["data_path"])
    records = df.to_dict(orient="records")
    metrics = compute_market_metrics(df)
    built_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    api_dir = os.path.join(cfg["output_dir"], "api")
    os.makedirs(api_dir, exist_ok=True)

    # 1. Endpoint de datos completo
    api_payload = {
        "metadata": {
            "project": "Mercado Libre Price Intelligence - iPhone 17 Pro Max",
            "version": cfg["app_version"],
            "environment": cfg["app_env"],
            "deploy_target": cfg["deploy_target"],
            "build_commit_sha": cfg["build_commit_sha"],
            "build_run_number": cfg["build_run_number"],
            "built_at_utc": built_at,
            "total_records": len(records),
            "currency": "COP",
            "metrics": metrics,
        },
        "data": records,
    }
    data_json_path = os.path.join(api_dir, "iphone17_data.json")
    with open(data_json_path, "w", encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)

    # 2. Endpoint de salud (Healthcheck estático para monitoreo cloud)
    health_payload = {
        "status": "ok",
        "service": "mercadolibre-iphone17pm-web",
        "version": cfg["app_version"],
        "environment": cfg["app_env"],
        "deploy_target": cfg["deploy_target"],
        "records_loaded": len(records),
        "build_commit_sha": cfg["build_commit_sha"],
        "built_at_utc": built_at,
    }
    health_json_path = os.path.join(api_dir, "health.json")
    with open(health_json_path, "w", encoding="utf-8") as f:
        json.dump(health_payload, f, ensure_ascii=False, indent=2)

    # 3. Aplicación Web SPA interactiva (index.html)
    html_content = render_web_html(records, metrics, cfg, built_at)
    index_html_path = os.path.join(cfg["output_dir"], "index.html")
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 4. Archivo .nojekyll para despliegue directo sin Jekyll en GitHub Pages
    nojekyll_path = os.path.join(cfg["output_dir"], ".nojekyll")
    with open(nojekyll_path, "w", encoding="utf-8") as f:
        f.write("")

    print(
        f"[CD SUCCESS] Artefactos v{cfg['app_version']} generados en '{cfg['output_dir']}' "
        f"(entorno={cfg['app_env']}, commit={cfg['build_commit_sha']}, registros={len(records)})."
    )
    return {
        "index_html": index_html_path,
        "data_json": data_json_path,
        "health_json": health_json_path,
        "metadata": api_payload["metadata"],
    }


if __name__ == "__main__":
    build_deployment_artifacts()
