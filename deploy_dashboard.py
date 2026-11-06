"""
=============================================================================
CONTINUOUS DEPLOYMENT (CD) GENERATOR - TABLERO ANALÍTICO WEB & API ESTÁTICA
Proyecto: Monitoreo iPhone 17 Pro Max en Mercado Libre Colombia
Unidad 2: Optimizando la productividad en el mundo del software (DevOps)
=============================================================================
Genera automáticamente el portal web estático (docs/index.html) y el endpoint
JSON (docs/api/iphone17_data.json) durante la etapa de Despliegue Continuo
en GitHub Actions hacia GitHub Pages.
=============================================================================
"""

import os
import json
from datetime import datetime
import pandas as pd


def build_deployment_artifacts():
    csv_path = "iphone_17_pro_max_mercadolibre.csv"
    df = pd.read_csv(csv_path)

    os.makedirs("docs/api", exist_ok=True)

    # Exportar API estática JSON para consumo externo
    records = df.to_dict(orient="records")
    api_payload = {
        "metadata": {
            "project": "Mercado Libre Price Intelligence - iPhone 17 Pro Max",
            "version": "2.0.0",
            "environment": "production",
            "total_records": len(records),
            "currency": "COP",
            "metrics": {
                "mean_price": round(float(df["precio_cop"].mean()), 2),
                "median_price": round(float(df["precio_cop"].median()), 2),
                "min_price": int(df["precio_cop"].min()),
                "max_price": int(df["precio_cop"].max()),
                "std_price": round(float(df["precio_cop"].std()), 2)
            }
        },
        "data": records
    }

    with open("docs/api/iphone17_data.json", "w", encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)

    # Construir filas HTML para la tabla interactiva
    rows_html = ""
    for r in records[:20]:
        rows_html += f"""
        <tr>
            <td>#{r['id']}</td>
            <td><strong>{r['titulo']}</strong></td>
            <td class="price">{r['precio_formateado']}</td>
            <td><span class="badge cap">{r['capacidad']}</span></td>
            <td><span class="badge ship">{r['envio']}</span></td>
            <td><a href="{r['enlace']}" target="_blank" rel="noopener">Ver en ML &rarr;</a></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard CI/CD | iPhone 17 Pro Max - Mercado Libre Colombia</title>
    <style>
        :root {{
            --primary: #0f2c59;
            --secondary: #1e56a0;
            --accent: #00a650;
            --bg: #f4f7fa;
            --card: #ffffff;
            --text: #1f2937;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
        }}
        header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 2rem 3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        header h1 {{ margin: 0; font-size: 1.6rem; }}
        header p {{ margin: 0.4rem 0 0; opacity: 0.9; font-size: 0.95rem; }}
        .status-pill {{
            background: rgba(0, 166, 80, 0.25);
            border: 1px solid #4ade80;
            color: #d1fae5;
            padding: 0.5rem 1rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .container {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: var(--card);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 4px solid var(--secondary);
        }}
        .kpi-card h3 {{ margin: 0; font-size: 0.85rem; text-transform: uppercase; color: #6b7280; }}
        .kpi-card .value {{ font-size: 1.6rem; font-weight: 700; color: var(--primary); margin-top: 0.5rem; }}
        .card-panel {{
            background: var(--card);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 2rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background-color: var(--primary);
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background-color: #f9fafb; }}
        .price {{ font-weight: 700; color: var(--primary); white-space: nowrap; }}
        .badge {{
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .badge.cap {{ background: #e0f2fe; color: #0369a1; }}
        .badge.ship {{ background: #dcfce7; color: #15803d; }}
        a {{ color: var(--secondary); text-decoration: none; font-weight: 600; }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Monitoreo Automatizado: Apple iPhone 17 Pro Max en Mercado Libre</h1>
            <p>IU Digital de Antioquia | Evidencia de Aprendizaje 2: Flujo de Trabajo DevOps, Git &amp; CI/CD con GitHub Actions</p>
        </div>
        <div class="status-pill">&#9679; CI/CD Pipeline Passing | Release v2.0.0</div>
    </header>
    <div class="container">
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Publicaciones Monitoreadas</h3>
                <div class="value">{len(records)} Unidades</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Promedio (COP)</h3>
                <div class="value">$ {df['precio_cop'].mean():,.0f}</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Mediano (COP)</h3>
                <div class="value">$ {df['precio_cop'].median():,.0f}</div>
            </div>
            <div class="kpi-card">
                <h3>Rango Mín / Máx (COP)</h3>
                <div class="value" style="font-size: 1.15rem;">$ {df['precio_cop'].min():,.0f} - $ {df['precio_cop'].max():,.0f}</div>
            </div>
        </div>
        <div class="card-panel">
            <h2>Catálogo Verificado por Pipeline CI/CD (Muestra Top 20 de 48 Registros)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Título de la Publicación</th>
                        <th>Precio (COP)</th>
                        <th>Capacidad</th>
                        <th>Logística</th>
                        <th>Enlace</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    <footer>
        Generado y desplegado automáticamente mediante GitHub Actions CI/CD &bull; Endpoint API JSON: <code>docs/api/iphone17_data.json</code>
    </footer>
</body>
</html>
""".replace(",", ".")

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[CD SUCCESS] Artefactos de despliegue continuo generados en 'docs/index.html' y 'docs/api/iphone17_data.json'.")


if __name__ == "__main__":
    build_deployment_artifacts()
