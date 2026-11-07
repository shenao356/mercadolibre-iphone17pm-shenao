"""
=============================================================================
CONTINUOUS DEPLOYMENT (CD) GENERATOR - TABLERO ANALÍTICO WEB & API ESTÁTICA
Proyecto: Monitoreo iPhone 17 Pro Max en Mercado Libre Colombia
Unidad 2: Optimizando la productividad en el mundo del software (DevOps)
=============================================================================
"""

import os
import json
import pandas as pd


def fmt_cop(val):
    return f"$ {val:,.0f}".replace(",", ".")


def build_deployment_artifacts():
    csv_path = "iphone_17_pro_max_mercadolibre.csv"
    df = pd.read_csv(csv_path)

    os.makedirs("docs/api", exist_ok=True)

    records = df.to_dict(orient="records")
    mean_val = float(df["precio_cop"].mean())
    median_val = float(df["precio_cop"].median())
    min_val = int(df["precio_cop"].min())
    max_val = int(df["precio_cop"].max())
    std_val = float(df["precio_cop"].std())

    api_payload = {
        "metadata": {
            "project": "Mercado Libre Price Intelligence - iPhone 17 Pro Max",
            "version": "2.2.0",
            "environment": "production",
            "total_records": len(records),
            "currency": "COP",
            "metrics": {
                "mean_price": round(mean_val, 2),
                "median_price": round(median_val, 2),
                "min_price": min_val,
                "max_price": max_val,
                "std_price": round(std_val, 2)
            }
        },
        "data": records
    }

    with open("docs/api/iphone17_data.json", "w", encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)

    mean_str = fmt_cop(mean_val)
    median_str = fmt_cop(median_val)
    min_str = fmt_cop(min_val)
    max_str = fmt_cop(max_val)
    std_str = fmt_cop(std_val)

    cap_256 = df[df["capacidad"] == "256GB"]
    cap_512 = df[df["capacidad"] == "512GB"]
    cap_1tb = df[df["capacidad"] == "1TB"]

    mean_256 = fmt_cop(cap_256["precio_cop"].mean()) if len(cap_256) else "$ 0"
    mean_512 = fmt_cop(cap_512["precio_cop"].mean()) if len(cap_512) else "$ 0"
    mean_1tb = fmt_cop(cap_1tb["precio_cop"].mean()) if len(cap_1tb) else "$ 0"

    rows_html = ""
    for r in records:
        cap_val = str(r['capacidad'])
        cap_class = "cap-256" if "256" in cap_val else ("cap-512" if "512" in cap_val else ("cap-1tb" if "1TB" in cap_val else "cap-other"))

        prev_price = str(r.get('precio_anterior', '-'))
        disc = str(r.get('descuento', '-'))
        if prev_price != '-' and prev_price != 'nan':
            price_cell_html = f"""
                <div class="old-price">Antes: <s>{prev_price}</s></div>
                <div class="curr-price">{r['precio_formateado']} <span class="disc-badge">{disc}</span></div>
            """
        else:
            price_cell_html = f"""<div class="curr-price">{r['precio_formateado']}</div>"""

        rows_html += f"""
        <tr>
            <td class="col-id">#{r['id']}</td>
            <td class="col-title">{r['titulo']}</td>
            <td class="col-price">{price_cell_html}</td>
            <td><span class="badge {cap_class}">{cap_val}</span></td>
            <td><span class="badge ship">{r['envio']}</span></td>
            <td><a class="btn-link" href="{r['enlace']}" target="_blank" rel="noopener">Abrir en ML &rarr;</a></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tablero de Precios | iPhone 17 Pro Max - Mercado Libre</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
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
            padding: 2rem 2.5rem;
            border-bottom: 5px solid #ffe600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .header-inner {{
            max-width: 1240px;
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
            margin: 0.4rem 0 0;
            color: #cbd5e1;
            font-size: 0.95rem;
        }}
        .status-pill {{
            background-color: #065f46;
            border: 2px solid #34d399;
            color: #ecfdf5;
            padding: 0.55rem 1.1rem;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 700;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
        }}
        .container {{
            max-width: 1240px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background-color: #ffffff;
            padding: 1.4rem 1.5rem;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            border-top: 5px solid #1e3e62;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.08);
        }}
        .kpi-card h3 {{
            margin: 0;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #334155;
            font-weight: 700;
        }}
        .kpi-card .value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.45rem;
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
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .cap-box {{
            background-color: #1e293b;
            color: #f8fafc;
            padding: 1.2rem 1.5rem;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.12);
        }}
        .cap-box .cap-label {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffe600;
        }}
        .cap-box .cap-desc {{
            font-size: 0.85rem;
            color: #cbd5e1;
        }}
        .cap-box .cap-count {{
            font-size: 1.5rem;
            font-weight: 800;
            background-color: #334155;
            color: #ffffff;
            padding: 0.35rem 0.85rem;
            border-radius: 8px;
        }}
        .card-panel {{
            background-color: #ffffff;
            padding: 1.75rem;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
            margin-bottom: 2rem;
            overflow-x: auto;
        }}
        .panel-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
            gap: 1rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1rem;
        }}
        .panel-header h2 {{
            margin: 0;
            font-size: 1.25rem;
            color: #0f172a;
        }}
        .search-input {{
            padding: 0.6rem 1rem;
            border: 2px solid #94a3b8;
            border-radius: 8px;
            font-size: 0.92rem;
            color: #0f172a;
            background-color: #f8fafc;
            min-width: 280px;
            font-weight: 500;
        }}
        .search-input:focus {{
            outline: none;
            border-color: #1e3e62;
            background-color: #ffffff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.92rem;
        }}
        th {{
            background-color: #0f172a;
            color: #ffffff;
            padding: 0.95rem 1rem;
            text-align: left;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.4px;
        }}
        td {{
            padding: 0.9rem 1rem;
            text-align: left;
            border-bottom: 1px solid #cbd5e1;
            color: #1e293b;
        }}
        tbody tr:nth-child(even) {{
            background-color: #f1f5f9;
        }}
        tbody tr:nth-child(odd) {{
            background-color: #ffffff;
        }}
        tbody tr:hover {{
            background-color: #dbeafe;
        }}
        .col-id {{
            font-weight: 700;
            color: #475569;
            width: 60px;
        }}
        .col-title {{
            font-weight: 600;
            color: #0f172a;
        }}
        .col-price {{
            white-space: nowrap;
        }}
        .old-price {{
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 2px;
        }}
        .curr-price {{
            font-weight: 800;
            color: #047857;
            font-size: 1.02rem;
        }}
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
            padding: 0.3rem 0.65rem;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }}
        .cap-256 {{
            background-color: #1e3a8a;
            color: #ffffff;
        }}
        .cap-512 {{
            background-color: #581c87;
            color: #ffffff;
        }}
        .cap-1tb {{
            background-color: #9a3412;
            color: #ffffff;
        }}
        .cap-other {{
            background-color: #475569;
            color: #ffffff;
        }}
        .badge.ship {{
            background-color: #065f46;
            color: #ffffff;
        }}
        .btn-link {{
            display: inline-block;
            background-color: #1e3e62;
            color: #ffffff;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.82rem;
            white-space: nowrap;
            transition: background-color 0.15s;
        }}
        .btn-link:hover {{
            background-color: #0b192c;
        }}
        footer {{
            background-color: #0f172a;
            color: #e2e8f0;
            text-align: center;
            padding: 1.75rem;
            margin-top: 3rem;
            font-size: 0.9rem;
        }}
        footer a {{
            color: #ffe600;
            text-decoration: none;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <div>
                <h1>📱 Monitoreo de Precios: Apple iPhone 17 Pro Max en Mercado Libre</h1>
                <p>IU Digital de Antioquia &bull; Evidencia de Aprendizaje 1 y 2 (Web Scraping, Git &amp; DevOps CI/CD)</p>
            </div>
            <div class="status-pill">&#10004; Pipeline CI/CD Activo &bull; 48 Artículos</div>
        </div>
    </header>

    <div class="container">
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Total Publicaciones</h3>
                <div class="value">{len(records)} Celulares</div>
                <div class="sub">Extraídos de Mercado Libre Colombia</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Promedio (Media)</h3>
                <div class="value">{mean_str}</div>
                <div class="sub">Desviación: {std_str} COP</div>
            </div>
            <div class="kpi-card">
                <h3>Precio Mediano (50%)</h3>
                <div class="value">{median_str}</div>
                <div class="sub">Punto medio del mercado</div>
            </div>
            <div class="kpi-card">
                <h3>Rango Mínimo / Máximo</h3>
                <div class="value" style="font-size: 1.2rem;">{min_str} / {max_str}</div>
                <div class="sub">Precios reales de venta (COP)</div>
            </div>
        </div>

        <div class="summary-grid">
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 256 GB</div>
                    <div class="cap-desc">Promedio: {mean_256} COP</div>
                </div>
                <div class="cap-count">{len(cap_256)}</div>
            </div>
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 512 GB</div>
                    <div class="cap-desc">Promedio: {mean_512} COP</div>
                </div>
                <div class="cap-count">{len(cap_512)}</div>
            </div>
            <div class="cap-box">
                <div>
                    <div class="cap-label">Capacidad 1 TB</div>
                    <div class="cap-desc">Promedio: {mean_1tb} COP</div>
                </div>
                <div class="cap-count">{len(cap_1tb)}</div>
            </div>
        </div>

        <div class="card-panel">
            <div class="panel-header">
                <h2>Catálogo Completo Extraído ({len(records)} Registros con Precios de Venta y Descuentos)</h2>
                <input type="text" id="tableFilter" class="search-input" placeholder="🔍 Filtrar por título, capacidad o precio..." onkeyup="filterRows()">
            </div>
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
        Desplegado automáticamente con <strong>GitHub Actions &amp; GitHub Pages</strong> &bull;
        Repositorio: <a href="https://github.com/shenao356/mercadolibre-iphone17pm-shenao" target="_blank">shenao356/mercadolibre-iphone17pm-shenao</a> &bull;
        API JSON: <a href="api/iphone17_data.json" target="_blank">api/iphone17_data.json</a>
    </footer>

    <script>
        function filterRows() {{
            var input = document.getElementById("tableFilter");
            var filter = input.value.toLowerCase();
            var rows = document.querySelectorAll("#productsTable tbody tr");
            rows.forEach(function(row) {{
                var text = row.innerText.toLowerCase();
                row.style.display = text.indexOf(filter) > -1 ? "" : "none";
            }});
        }}
    </script>
</body>
</html>
"""

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[CD SUCCESS] Tablero web actualizado con precios reales de venta y descuentos en 'docs/index.html'.")


if __name__ == "__main__":
    build_deployment_artifacts()
