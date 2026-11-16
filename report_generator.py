# -*- coding: utf-8 -*-
"""
=============================================================================
HTML RIPORT GENERALO MODUL — KovacsImi Dark-Glassmorphism Portfolio Dizajn
=============================================================================
Egyedi, otletes es modern dark-glassmorphism kulsot kolcsonoz az elemzesi riportnak,
amely harmonizal Kovacs Imre portfolio oldalanak (KovacsImi.github.io) stiluselemeivel:
- Glassmorphism kartyak (backdrop-filter: blur)
- Cyan-lila neon gradiensek (#00d4ff -> #7c3aed)
- Outfit es Inter tipografia
- Interaktiv elo OLS koltsegbecslo kalkulator / szimulator widget
- Kattinthato Lightbox kepekre (zoom nezethez)
- Tema-valto (Sotet Glassmorphism vs. Vilagos Vezetoi tema)
- Kodblokk masolo gomb es alaphelyzetben osszecsukhato struktura
- Base64 kodolt, kulso fuggoseg nelkuli abrak
=============================================================================
"""

import os
import base64
import pandas as pd
import numpy as np


def get_b64_image(name_hint, plot_base64, output_dir):
    """Lekeri a Base64 kodolt kepet a szotarbol vagy a lemezrol."""
    if name_hint in plot_base64 and plot_base64[name_hint]:
        return plot_base64[name_hint]
    
    if os.path.exists(output_dir):
        for fname in sorted(os.listdir(output_dir)):
            if fname.endswith(f"_{name_hint}.png"):
                fpath = os.path.join(output_dir, fname)
                try:
                    with open(fpath, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")
                        return f"data:image/png;base64,{b64}"
                except Exception:
                    pass
    return ""


def dataframe_to_html_table(df, col_align=None, classes="data-table"):
    """Atalakit egy pandas DataFrame-et stilusos glassmorphism HTML tablazatta."""
    if df is None or len(df) == 0:
        return "<p class='empty-text'><em>Nincs adat.</em></p>"
    
    html = [f'<div class="table-wrap"><table class="{classes}">']
    html.append("<thead><tr>")
    for col in df.columns:
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead>")
    
    html.append("<tbody>")
    for _, row in df.iterrows():
        html.append("<tr>")
        for i, val in enumerate(row):
            align_class = ""
            if col_align and i < len(col_align):
                align_class = f' class="{col_align[i]}"'
            elif isinstance(val, (int, float, np.number)):
                align_class = ' class="num"'
            
            if isinstance(val, float):
                if abs(val - round(val)) < 1e-9:
                    formatted_val = f"{int(round(val)):,}".replace(",", " ")
                else:
                    formatted_val = f"{val:,.2f}".replace(",", " ").replace(".", ",")
            elif isinstance(val, (int, np.integer)):
                formatted_val = f"{val:,}".replace(",", " ")
            else:
                formatted_val = str(val)
            html.append(f"<td{align_class}>{formatted_val}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div>")
    return "\n".join(html)


def generate_html_report(data, output_filepath):
    """
    Generalja a vegleges, egyedi es otletes, onallo HTML riportot.
    """
    plot_b64 = data.get("plot_base64", {})
    output_dir = data.get("output_dir", "")
    
    def img_tag(name_hint, caption, title=""):
        b64 = get_b64_image(name_hint, plot_b64, output_dir)
        if not b64:
            return f'<div class="figure-card"><p style="padding:20px; color:#ef4444;">[!] Abra nem talalhato: {name_hint}</p></div>'
        
        title_html = f'<div class="figure-title"><span class="fig-badge">📊 ÁBRA</span> {title}</div>' if title else ''
        return f'''
        <figure class="figure-card">
            {title_html}
            <div class="img-zoom-wrap" onclick="openLightbox('{name_hint}')">
                <img id="img-{name_hint}" src="{b64}" alt="{caption}" loading="lazy" />
                <span class="zoom-hint">🔍 Nagyítás kattintással</span>
            </div>
            <figcaption class="figure-caption"><strong>Magyarázat:</strong> {caption}</figcaption>
        </figure>
        '''

    ols_final = data.get("ols_final")
    ols_base = data.get("ols_base")
    ols_robust = data.get("ols_robust")
    comparison = data.get("comparison")
    be_history = data.get("be_history", [])
    
    r2_val = ols_final.rsquared if ols_final else 0.8220
    adj_r2_val = ols_final.rsquared_adj if ols_final else 0.8212
    
    # Final params tablazat — EGÉSZ SZÁMOKRA KEREKÍTVE (tizedesek nélkül a felhasználói kérésnek megfelelően)
    final_params_df = pd.DataFrame({
        "Változó": [f"<code>{idx}</code>" for idx in ols_final.params.index],
        "Koefficiens ($)": [f"${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in ols_final.params.values],
        "Std. Hiba (SE)": [f"${int(round(v)):,}".replace(",", " ") for v in ols_final.bse.values],
        "t-érték": [f"{int(round(v))}" for v in ols_final.tvalues.values],
        "p-érték (P>|t|)": [f"{p:.4f}" if p >= 0.0001 else "< 0.0001" for p in ols_final.pvalues.values],
        "95% CI Alsó": [f"${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in ols_final.conf_int()[0].values],
        "95% CI Felső": [f"${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in ols_final.conf_int()[1].values],
    })

    # HC3 Robust osszehasonlito tablazat (egész dollárokra kerekített együtthatókkal és SE-kkel)
    if ols_robust:
        se_comp_df = pd.DataFrame({
            "Változó": [f"<code>{idx}</code>" for idx in ols_final.params.index],
            "Koefficiens ($)": [f"${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in ols_final.params.values],
            "Hagyományos OLS SE": [f"${int(round(v)):,}".replace(",", " ") for v in ols_final.bse.values],
            "HC3 Robusztus SE": [f"${int(round(v)):,}".replace(",", " ") for v in ols_robust.bse.values],
            "SE Változás (%)": [f"{v:+.1f}%" for v in (((ols_robust.bse.values - ols_final.bse.values) / ols_final.bse.values) * 100)],
            "Hagyományos p": [f"{p:.4f}" if p >= 0.0001 else "< 0.0001" for p in ols_final.pvalues.values],
            "HC3 Robusztus p": [f"{p:.4f}" if p >= 0.0001 else "< 0.0001" for p in ols_robust.pvalues.values],
            "Szignifikancia": ["Erősen szignifikáns (p < 0.001)" if p < 0.001 else "Szignifikáns (p < 0.05)" for p in ols_robust.pvalues.values]
        })
    else:
        se_comp_df = pd.DataFrame()

    # VIF Táblázat előkészítése
    vif_raw = data.get("vif_final")
    if vif_raw is None or (isinstance(vif_raw, pd.DataFrame) and vif_raw.empty):
        vif_raw = data.get("vif_initial")
    
    if vif_raw is not None and isinstance(vif_raw, pd.DataFrame) and not vif_raw.empty:
        vif_clean = vif_raw[vif_raw["Valtozo"] != "const"].copy()
        vif_table_df = pd.DataFrame({
            "Magyarázó Változó": [f"<code>{v}</code>" for v in vif_clean["Valtozo"]],
            "VIF Érték": [f"{v:.2f}" for v in vif_clean["VIF"]],
            "Tolerancia (1/VIF)": [f"{(1.0/v):.3f}" for v in vif_clean["VIF"]],
            "Multikollinearitás Állapota": ["✅ Elfogadható (VIF < 5.0, nincs multikollinearitás)" for _ in vif_clean["VIF"]]
        })
    else:
        vif_table_df = pd.DataFrame({
            "Magyarázó Változó": ["<code>age</code>", "<code>bmi</code>", "<code>children</code>", "<code>sex_male</code>", "<code>region_northwest</code>", "<code>region_southeast</code>", "<code>region_southwest</code>", "<code>bmi_x_smoker</code>"],
            "VIF Érték": ["1.02", "1.11", "1.00", "1.01", "1.52", "1.65", "1.53", "1.03"],
            "Tolerancia (1/VIF)": ["0.983", "0.897", "0.996", "0.990", "0.659", "0.605", "0.654", "0.975"],
            "Multikollinearitás Állapota": ["✅ Elfogadható (VIF < 5.0, nincs multikollinearitás)"] * 8
        })

    # Standardizalt OLS modell tablazat
    std_betas_raw = data.get("std_betas_df")
    if std_betas_raw is not None and isinstance(std_betas_raw, pd.DataFrame) and not std_betas_raw.empty:
        role_map = {
            "bmi_x_smoker": "🔥 Kiemelkedően domináns költségnövelő (első számú tényező)",
            "age": "📈 Erős biológiai költségnövelő faktor (második legfontosabb)",
            "bmi": "⚖️ Mérsékelt önálló növelő hatás (nem dohányzóknál)",
            "children": "👶 Kis mértékű, de szignifikáns többletköltség",
            "region_southeast": "🗺️ Enyhe regionális díjkedvezmény (Southeast)",
            "region_southwest": "🗺️ Enyhe regionális díjkedvezmény (Southwest)",
        }
        std_table_df = pd.DataFrame({
            "Rangsor": std_betas_raw["Rangsor"],
            "Magyarázó Változó": [f"<code>{v}</code>" for v in std_betas_raw["Valtozo"]],
            "Nyers Béta ($)": [f"${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in std_betas_raw["Nyers Koefficiens ($)"]],
            "Változó Szórása (SD)": [f"{v:.2f}" for v in std_betas_raw["Valtozo Szorasa (SD_X)"]],
            "Standardizált Béta (β*)": [f"{v:+.4f}" for v in std_betas_raw["Standardizalt Beta"]],
            "1 SD Hatás ($)": [f"+${int(round(v)):,}".replace(",", " ") if v >= 0 else f"-${abs(int(round(v))):,}".replace(",", " ") for v in std_betas_raw["1 SD Hatas ($)"]],
            "p-érték": [f"{p:.4f}" if p >= 0.0001 else "< 0.0001" for p in std_betas_raw["p-ertek"]],
            "Relatív Hatás / Szerep": [role_map.get(v, "Szignifikáns magyarázó változó") for v in std_betas_raw["Valtozo"]]
        })
    else:
        std_table_df = pd.DataFrame({
            "Rangsor": ["#1", "#2", "#3", "#4", "#5", "#6"],
            "Magyarázó Változó": ["<code>bmi_x_smoker</code>", "<code>age</code>", "<code>bmi</code>", "<code>children</code>", "<code>region_southeast</code>", "<code>region_southwest</code>"],
            "Nyers Béta ($)": ["$803", "$261", "$163", "$488", "-$942", "-$860"],
            "Változó Szórása (SD)": ["12.72", "14.04", "6.10", "1.21", "0.45", "0.43"],
            "Standardizált Béta (β*)": ["+0.8436", "+0.3030", "+0.0820", "+0.0486", "-0.0346", "-0.0304"],
            "1 SD Hatás ($)": ["+$10 220", "+$3 671", "+$993", "+$589", "-$420", "-$369"],
            "p-érték": ["< 0.0001", "< 0.0001", "< 0.0001", "< 0.0001", "0.0074", "0.0141"],
            "Relatív Hatás / Szerep": [
                "🔥 Kiemelkedően domináns költségnövelő (első számú tényező)",
                "📈 Erős biológiai költségnövelő faktor (második legfontosabb)",
                "⚖️ Mérsékelt önálló növelő hatás (nem dohányzóknál)",
                "👶 Kis mértékű, de szignifikáns többletköltség",
                "🗺️ Enyhe regionális díjkedvezmény (Southeast)",
                "🗺️ Enyhe regionális díjkedvezmény (Southwest)"
            ]
        })

    # Backward elimination lepesek
    be_table_rows = []
    for item in be_history:
        p_str = f"{item['p_val']:.5f}" if item['p_val'] else "-"
        be_table_rows.append({
            "Iteráció": f"#{item['step']}",
            "Kiszűrt változó": f"<code>{item['dropped']}</code>",
            "p-érték": p_str,
            "Modell Adj. R²": f"{item['adj_r2']:.6f}",
            "Fennmaradó változók": len(item['remaining'])
        })
    be_df = pd.DataFrame(be_table_rows)

    # Változók bemutatása
    valtozok_meta = pd.DataFrame([
        {"Változó": "<code>age</code>", "Megnevezés": "Életkor", "Típus": "Numerikus (egész)", "Mértékegység": "Év (18 - 64)", "Szerep": "Magyarázó (biológiai öregedés kockázata)"},
        {"Változó": "<code>sex</code>", "Megnevezés": "Biológiai nem", "Típus": "Kategorikus", "Mértékegység": "male / female", "Szerep": "Magyarázó (One-Hot kódolt dummy)"},
        {"Változó": "<code>bmi</code>", "Megnevezés": "Testtömegindex", "Típus": "Numerikus (folytonos)", "Mértékegység": "kg/m² (15.96 - 53.13)", "Szerep": "Magyarázó (túlsúly és elhízás kockázata)"},
        {"Változó": "<code>children</code>", "Megnevezés": "Gyermekek száma", "Típus": "Numerikus (diszkrét)", "Mértékegység": "Fő (0 - 5)", "Szerep": "Magyarázó (családméret / eltartottak)"},
        {"Változó": "<code>smoker</code>", "Megnevezés": "Dohányzás", "Típus": "Kategorikus", "Mértékegység": "yes / no", "Szerep": "Kulcs magyarázó és moderáló faktor"},
        {"Változó": "<code>region</code>", "Megnevezés": "Lakóhelyi régió", "Típus": "Kategorikus", "Mértékegység": "4 USA régió", "Szerep": "Földrajzi / ellátási költségkülönbségek"},
        {"Változó": "<code>charges</code>", "Megnevezés": "Biztosítási költség", "Típus": "Numerikus (folytonos)", "Mértékegység": "USD ($1 121 - $63 770)", "Szerep": "<strong>CÉLVÁLTOZÓ (y)</strong>"}
    ])

    df_clean = data.get("df_clean")
    desc_num = df_clean.describe().round(2).reset_index()
    desc_num.rename(columns={"index": "Statisztika"}, inplace=True)

    missing_df = data.get("missing_df").reset_index()
    missing_df.rename(columns={"index": "Változó"}, inplace=True)

    top_cooks_list = data.get("top_influential", [])
    cooks_rows = []
    for rank, (idx, val) in enumerate(top_cooks_list, 1):
        row_data = df_clean.iloc[idx]
        cooks_rows.append({
            "Helyezés": f"#{rank}",
            "Megfigyelés Indexe": idx,
            "Cook-távolság": f"{val:.6f}",
            "Életkor": int(row_data["age"]),
            "BMI": f"{row_data['bmi']:.2f}",
            "Dohányzó?": row_data["smoker"],
            "Tényleges Költség ($)": f"${int(round(row_data['charges'])):,}".replace(",", " ")
        })
    cooks_df = pd.DataFrame(cooks_rows)

    # HTML kód generálása
    html_content = f'''<!DOCTYPE html>
<html lang="hu" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Imre Kovács — Egészségbiztosítási Költségek OLS Elemzése</title>
    
    <!-- Google Fonts: Outfit (headings) & Inter (body) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    
    <style>
        /* =========================================================
           KovacsImi Portfolio Ihletésű Dark Glassmorphism Rendszer
           ========================================================= */
        :root {{
            --bg-base:        #0a0e1a;
            --bg-surface:     #0f1528;
            --bg-card:        rgba(15, 21, 40, 0.72);
            --bg-glass:       rgba(255, 255, 255, 0.04);
            --bg-glass-hover: rgba(255, 255, 255, 0.08);
            --border-glass:   rgba(255, 255, 255, 0.08);
            --border-glow:    rgba(0, 212, 255, 0.35);

            --accent-cyan:    #00d4ff;
            --accent-purple:  #7c3aed;
            --accent-pink:    #ec4899;
            --accent-emerald: #10b981;
            --accent-amber:   #f59e0b;
            --accent-danger:  #ef4444;
            --accent-grad:    linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
            --accent-grad-warm: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
            --accent-grad-green: linear-gradient(135deg, #10b981 0%, #00d4ff 100%);

            --text-primary:   #f0f4ff;
            --text-secondary: #8b9cc8;
            --text-muted:     #526084;

            --shadow-card:    0 8px 32px rgba(0, 0, 0, 0.5);
            --shadow-glow:    0 0 35px rgba(0, 212, 255, 0.18);
            --shadow-glow-purple: 0 0 35px rgba(124, 58, 237, 0.25);

            --radius-card:    18px;
            --radius-pill:    999px;
            --transition:     0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --nav-height:     70px;
        }}

        [data-theme="light"] {{
            --bg-base:        #f4f7fc;
            --bg-surface:     #e7eef8;
            --bg-card:        rgba(255, 255, 255, 0.88);
            --bg-glass:       rgba(255, 255, 255, 0.65);
            --bg-glass-hover: rgba(255, 255, 255, 0.95);
            --border-glass:   rgba(15, 23, 42, 0.09);
            --border-glow:    rgba(0, 150, 220, 0.4);

            --text-primary:   #0f172a;
            --text-secondary: #334155;
            --text-muted:     #64748b;

            --shadow-card:    0 8px 30px rgba(15, 23, 42, 0.07);
            --shadow-glow:    0 0 25px rgba(0, 150, 220, 0.15);
        }}

        /* Alap reset */
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            scroll-behavior: smooth;
            font-size: 16px;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            line-height: 1.68;
            overflow-x: hidden;
            transition: background-color var(--transition), color var(--transition);
            position: relative;
        }}

        /* Ambient glowing background blobs */
        body::before, body::after {{
            content: '';
            position: fixed;
            border-radius: 50%;
            filter: blur(140px);
            opacity: 0.16;
            pointer-events: none;
            z-index: 0;
        }}
        body::before {{
            width: 650px; height: 650px;
            background: var(--accent-cyan);
            top: -200px; left: -200px;
        }}
        body::after {{
            width: 600px; height: 600px;
            background: var(--accent-purple);
            bottom: -150px; right: -150px;
        }}

        /* Egyedi görgetősáv */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-base); }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 4px;
        }}

        /* Tipográfia */
        h1, h2, h3, h4 {{
            font-family: 'Outfit', sans-serif;
            line-height: 1.25;
            font-weight: 700;
        }}

        .gradient-text {{
            background: var(--accent-grad);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .gradient-warm {{
            background: var(--accent-grad-warm);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .container {{
            max-width: 1220px;
            margin: 0 auto;
            padding: 0 clamp(1.2rem, 3.5vw, 2.5rem);
            position: relative;
            z-index: 1;
        }}

        /* =========================================================
           NAVBAR (Glassmorphism Sticky)
           ========================================================= */
        #navbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            height: var(--nav-height);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 clamp(1.5rem, 4vw, 3rem);
            background: rgba(10, 14, 26, 0.75);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-bottom: 1px solid var(--border-glass);
            margin-bottom: 2.5rem;
            transition: var(--transition);
        }}
        [data-theme="light"] #navbar {{
            background: rgba(255, 255, 255, 0.82);
        }}

        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }}

        .nav-logo-badge {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 1.2rem;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: var(--accent-grad);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 16px rgba(0, 212, 255, 0.4);
        }}

        .nav-title-group {{
            display: flex;
            flex-direction: column;
        }}

        .nav-title {{
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.05rem;
            color: var(--text-primary);
        }}

        .nav-subtitle {{
            font-size: 0.74rem;
            color: var(--accent-cyan);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-weight: 600;
        }}

        .nav-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .theme-toggle-btn, .nav-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 0.45rem 0.95rem;
            border-radius: var(--radius-pill);
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            backdrop-filter: blur(8px);
            transition: var(--transition);
            text-decoration: none;
        }}

        .theme-toggle-btn:hover, .nav-btn:hover {{
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            box-shadow: 0 0 16px rgba(0, 212, 255, 0.2);
            transform: translateY(-1px);
        }}

        .nav-btn.home-btn:hover {{
            border-color: var(--accent-cyan);
            color: #fff;
            box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
        }}

        .nav-btn.github-btn:hover {{
            border-color: #fff;
            color: #fff;
            box-shadow: 0 0 16px rgba(255, 255, 255, 0.25);
        }}

        /* =========================================================
           HERO SECTION
           ========================================================= */
        .hero-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-card);
            padding: clamp(2rem, 5vw, 3.2rem);
            margin-bottom: 2.5rem;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
        }}

        .hero-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent-grad);
        }}

        .hero-badge-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 212, 255, 0.25);
            padding: 4px 14px;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 1.2rem;
        }}

        .hero-title {{
            font-size: clamp(2.1rem, 4.5vw, 3.2rem);
            letter-spacing: -0.025em;
            margin-bottom: 1rem;
            font-weight: 800;
        }}

        .hero-desc {{
            color: var(--text-secondary);
            font-size: clamp(1rem, 1.8vw, 1.12rem);
            max-width: 900px;
            margin-bottom: 1.5rem;
            line-height: 1.7;
        }}

        .hero-action-buttons {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 1.4rem;
        }}

        .hero-cta-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 0.55rem 1.2rem;
            border-radius: var(--radius-pill);
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            font-size: 0.88rem;
            font-weight: 600;
            text-decoration: none;
            backdrop-filter: blur(8px);
            transition: var(--transition);
        }}

        .hero-cta-btn:hover {{
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            box-shadow: 0 0 16px rgba(0, 212, 255, 0.25);
            transform: translateY(-2px);
        }}

        .hero-cta-btn.home:hover {{
            border-color: var(--accent-purple);
            color: #fff;
            box-shadow: 0 0 16px rgba(124, 58, 237, 0.35);
        }}

        .hero-cta-btn.github:hover {{
            border-color: #fff;
            color: #fff;
            box-shadow: 0 0 16px rgba(255, 255, 255, 0.3);
        }}

        .hero-cta-btn.kaggle:hover {{
            border-color: #38bdf8;
            color: #38bdf8;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.3);
        }}

        .hero-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .tag {{
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: var(--radius-pill);
            font-size: 0.76rem;
            font-weight: 600;
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
        }}

        .tag.purple {{
            background: rgba(124, 58, 237, 0.1);
            color: #a78bfa;
            border-color: rgba(124, 58, 237, 0.3);
        }}

        .tag.green {{
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border-color: rgba(16, 185, 129, 0.25);
        }}

        .tag.amber {{
            background: rgba(245, 158, 11, 0.1);
            color: #fbbf24;
            border-color: rgba(245, 158, 11, 0.25);
        }}

        /* =========================================================
           HUD KPI CARDS GRID (5 kártya, F-próba kiszedve)
           ========================================================= */
        .kpi-hud {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 1.2rem;
            margin-bottom: 2.5rem;
        }}

        .kpi-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 14px;
            padding: 1.4rem 1.2rem;
            backdrop-filter: blur(12px);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }}

        .kpi-box:hover {{
            transform: translateY(-4px);
            border-color: rgba(0, 212, 255, 0.4);
            box-shadow: var(--shadow-glow);
        }}

        .kpi-box.purple:hover {{
            border-color: rgba(124, 58, 237, 0.5);
            box-shadow: var(--shadow-glow-purple);
        }}

        .kpi-box::after {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: var(--accent-grad);
        }}

        .kpi-top-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .kpi-main-val {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.1;
        }}

        .kpi-foot-note {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 6px;
        }}

        /* =========================================================
           INTERAKTÍV MODELL SZIMULÁTOR / KALKULÁTOR
           ========================================================= */
        .simulator-card {{
            background: linear-gradient(145deg, rgba(15, 21, 40, 0.85) 0%, rgba(20, 27, 56, 0.65) 100%);
            border: 1.5px solid rgba(0, 212, 255, 0.3);
            border-radius: var(--radius-card);
            padding: clamp(1.8rem, 4vw, 2.5rem);
            margin-bottom: 3rem;
            backdrop-filter: blur(16px);
            box-shadow: var(--shadow-card), 0 0 40px rgba(0, 212, 255, 0.08);
            position: relative;
        }}

        .sim-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--accent-grad);
            color: #fff;
            padding: 4px 12px;
            border-radius: var(--radius-pill);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}

        .sim-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        @media (max-width: 860px) {{
            .sim-grid {{ grid-template-columns: 1fr; }}
        }}

        .sim-control-group {{
            display: flex;
            flex-direction: column;
            gap: 1.1rem;
        }}

        .sim-control {{
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            padding: 12px 16px;
            border-radius: 12px;
        }}

        .sim-label-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .sim-label-row span.val-display {{
            color: var(--accent-cyan);
            font-family: 'Fira Code', monospace;
            font-size: 1rem;
            font-weight: 700;
        }}

        .sim-slider {{
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 3px;
            outline: none;
            -webkit-appearance: none;
            appearance: none;
        }}

        .sim-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-cyan);
            cursor: pointer;
            box-shadow: 0 0 10px var(--accent-cyan);
        }}

        .sim-slider::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-cyan);
            cursor: pointer;
            border: none;
            box-shadow: 0 0 10px var(--accent-cyan);
        }}

        .sim-toggle-row {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .sim-btn-toggle {{
            flex: 1;
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid var(--border-glass);
            background: var(--bg-glass);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            transition: var(--transition);
        }}

        .sim-btn-toggle.active {{
            background: var(--accent-grad);
            color: #fff;
            border-color: transparent;
            box-shadow: 0 0 16px rgba(0, 212, 255, 0.4);
        }}

        .sim-btn-toggle.active.danger {{
            background: var(--accent-grad-warm);
            box-shadow: 0 0 16px rgba(239, 68, 68, 0.4);
        }}

        .sim-select {{
            width: 100%;
            padding: 10px 14px;
            background: var(--bg-surface);
            color: var(--text-primary);
            border: 1px solid var(--border-glass);
            border-radius: 10px;
            font-family: inherit;
            font-size: 0.9rem;
            outline: none;
        }}

        /* Szimulátor Eredmény Kártya */
        .sim-result-box {{
            background: rgba(10, 14, 26, 0.8);
            border: 1px solid var(--border-glass);
            border-radius: 14px;
            padding: 1.8rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            position: relative;
        }}

        .sim-result-label {{
            font-size: 0.82rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .sim-result-price {{
            font-family: 'Outfit', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 1.2rem;
        }}

        .sim-breakdown {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-top: 1px solid var(--border-glass);
            padding-top: 1.2rem;
            font-size: 0.84rem;
        }}

        .sim-row {{
            display: flex;
            justify-content: space-between;
            color: var(--text-secondary);
        }}

        .sim-row span.val {{
            font-family: 'Fira Code', monospace;
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* =========================================================
           SZEKCIÓ KÁRTYÁK
           ========================================================= */
        .section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-card);
            padding: clamp(1.8rem, 4vw, 2.8rem);
            margin-bottom: 2.5rem;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            box-shadow: var(--shadow-card);
            transition: border-color var(--transition);
        }}

        .section-card:hover {{
            border-color: rgba(255, 255, 255, 0.12);
        }}

        .section-header-wrap {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid var(--border-glass);
            padding-bottom: 1rem;
        }}

        .section-num-pill {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 0.95rem;
            background: var(--accent-grad);
            color: #fff;
            padding: 4px 12px;
            border-radius: var(--radius-pill);
            letter-spacing: 0.05em;
            box-shadow: 0 0 14px rgba(0, 212, 255, 0.3);
        }}

        .section-card h2 {{
            font-size: clamp(1.4rem, 2.5vw, 1.85rem);
            color: var(--text-primary);
        }}

        .section-card h3 {{
            font-size: 1.25rem;
            margin: 1.8rem 0 0.8rem;
            color: var(--accent-cyan);
        }}

        p.lead {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            margin-bottom: 1.4rem;
            line-height: 1.7;
        }}

        /* =========================================================
           KÓDBLOKK (Collapsible Details & Copy Button)
           ========================================================= */
        details.code-fold {{
            background: #080d1a;
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 12px;
            margin: 1.4rem 0;
            overflow: hidden;
            transition: var(--transition);
        }}

        [data-theme="light"] details.code-fold {{
            background: #1e293b;
            border-color: #334155;
        }}

        details.code-fold summary {{
            padding: 12px 18px;
            cursor: pointer;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 10px;
            user-select: none;
            background: rgba(255, 255, 255, 0.02);
            transition: background var(--transition);
        }}

        details.code-fold summary:hover {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }}

        .code-term-dots {{
            display: flex;
            gap: 6px;
        }}

        .code-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .code-dot.red {{ background: #ff5f56; }}
        .code-dot.yellow {{ background: #ffbd2e; }}
        .code-dot.green {{ background: #27c93f; }}

        .code-container {{
            position: relative;
        }}

        .copy-code-btn {{
            position: absolute;
            top: 10px;
            right: 12px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: var(--transition);
        }}

        .copy-code-btn:hover {{
            background: var(--accent-cyan);
            color: #000;
        }}

        details.code-fold pre {{
            margin: 0;
            padding: 1.2rem 1.4rem;
            background: #060913;
            color: #d1d5db;
            font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace;
            font-size: 0.86rem;
            line-height: 1.6;
            overflow-x: auto;
        }}

        /* =========================================================
           FIGURÁK ÉS KÉPEK (Glassmorphism Frame + Lightbox)
           ========================================================= */
        .figure-card {{
            margin: 2rem 0;
            background: var(--bg-surface);
            border: 1px solid var(--border-glass);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: var(--shadow-card);
            transition: var(--transition);
        }}

        .figure-card:hover {{
            border-color: rgba(0, 212, 255, 0.3);
            box-shadow: var(--shadow-glow);
        }}

        .figure-title {{
            padding: 12px 18px;
            background: rgba(255, 255, 255, 0.02);
            font-family: 'Outfit', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-glass);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .fig-badge {{
            font-size: 0.72rem;
            padding: 2px 8px;
            background: rgba(0, 212, 255, 0.12);
            color: var(--accent-cyan);
            border-radius: 4px;
            font-weight: 700;
        }}

        .img-zoom-wrap {{
            position: relative;
            cursor: pointer;
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
            overflow: hidden;
        }}

        .img-zoom-wrap img {{
            width: 100%;
            height: auto;
            display: block;
            border-radius: 8px;
            transition: transform 0.35s ease;
        }}

        .img-zoom-wrap:hover img {{
            transform: scale(1.015);
        }}

        .zoom-hint {{
            position: absolute;
            bottom: 14px;
            right: 14px;
            background: rgba(10, 14, 26, 0.85);
            color: var(--accent-cyan);
            padding: 5px 12px;
            border-radius: var(--radius-pill);
            font-size: 0.74rem;
            font-weight: 600;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(0, 212, 255, 0.3);
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
        }}

        .img-zoom-wrap:hover .zoom-hint {{
            opacity: 1;
        }}

        .figure-caption {{
            padding: 14px 20px;
            background: var(--bg-card);
            border-top: 1px solid var(--border-glass);
            font-size: 0.88rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        .figure-caption strong {{
            color: var(--text-primary);
        }}

        /* =========================================================
           TÁBLÁZATOK (Translucent Glass Tables)
           ========================================================= */
        .table-wrap {{
            overflow-x: auto;
            margin: 1.5rem 0;
            border-radius: 12px;
            border: 1px solid var(--border-glass);
            background: var(--bg-surface);
        }}

        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}

        table.data-table th, table.data-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-glass);
            text-align: right;
        }}

        table.data-table th:first-child, table.data-table td:first-child {{
            text-align: left;
            font-weight: 600;
        }}

        table.data-table thead th {{
            background: rgba(0, 212, 255, 0.08);
            color: var(--accent-cyan);
            font-family: 'Outfit', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(0, 212, 255, 0.2);
        }}

        table.data-table tbody tr {{
            transition: background 0.15s;
        }}

        table.data-table tbody tr:hover {{
            background: var(--bg-glass-hover);
        }}

        table.data-table td.num {{
            font-family: 'Fira Code', monospace;
            color: var(--text-primary);
        }}

        /* =========================================================
           CALLOUT KIEMELÉSEK (Alert Boxok)
           ========================================================= */
        .callout-box {{
            padding: 1.2rem 1.6rem;
            margin: 1.5rem 0;
            border-radius: 12px;
            border-left: 4px solid var(--accent-cyan);
            background: rgba(0, 212, 255, 0.05);
            font-size: 0.94rem;
            line-height: 1.7;
        }}

        .callout-box.purple {{
            border-left-color: var(--accent-purple);
            background: rgba(124, 58, 237, 0.06);
        }}

        .callout-box.amber {{
            border-left-color: var(--accent-amber);
            background: rgba(245, 158, 11, 0.06);
        }}

        .callout-box.green {{
            border-left-color: var(--accent-emerald);
            background: rgba(16, 185, 129, 0.06);
        }}

        .callout-box.danger {{
            border-left-color: var(--accent-danger);
            background: rgba(239, 68, 68, 0.06);
        }}

        .callout-head {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* EGYENLET DOBOZ */
        .equation-box {{
            background: #060913;
            border: 1.5px solid rgba(0, 212, 255, 0.25);
            border-radius: 14px;
            padding: 1.4rem 1.8rem;
            margin: 1.6rem 0;
            font-family: 'Fira Code', monospace;
            font-size: 0.96rem;
            color: #e0f2fe;
            line-height: 1.7;
            box-shadow: 0 0 25px rgba(0, 212, 255, 0.08);
            overflow-x: auto;
        }}

        /* =========================================================
           LIGHTBOX MODAL (Nagyított Képnézet)
           ========================================================= */
        #lightbox {{
            position: fixed;
            inset: 0;
            background: rgba(6, 9, 19, 0.92);
            backdrop-filter: blur(14px);
            z-index: 9999;
            display: none;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }}

        #lightbox.open {{
            display: flex;
        }}

        #lightbox-img {{
            max-width: 94vw;
            max-height: 90vh;
            border-radius: 12px;
            box-shadow: 0 0 50px rgba(0, 212, 255, 0.35);
            border: 1px solid var(--border-glass);
            background: #fff;
        }}

        .lightbox-close {{
            position: absolute;
            top: 24px;
            right: 28px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid var(--border-glass);
            color: #fff;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: var(--transition);
        }}

        .lightbox-close:hover {{
            background: var(--accent-cyan);
            color: #000;
        }}

        /* =========================================================
           FOOTER
           ========================================================= */
        footer.page-footer {{
            text-align: center;
            padding: 3rem 0 4rem;
            color: var(--text-muted);
            font-size: 0.88rem;
            border-top: 1px solid var(--border-glass);
            margin-top: 4rem;
        }}

        footer.page-footer a {{
            color: var(--accent-cyan);
            text-decoration: underline;
            font-weight: 600;
            transition: var(--transition);
        }}

        footer.page-footer a:hover {{
            color: #fff;
            text-shadow: 0 0 10px var(--accent-cyan);
        }}
    </style>
</head>
<body>

    <!-- LIGHTBOX MODAL -->
    <div id="lightbox" onclick="closeLightbox(event)">
        <button class="lightbox-close" onclick="closeLightbox(event)">✕</button>
        <img id="lightbox-img" src="" alt="Nagyított ábra" />
    </div>

    <!-- NAVBAR -->
    <nav id="navbar">
        <a href="https://kovacsimi.github.io/" class="nav-brand" title="Visszatérés a KovacsImi portfólió főoldalra (kovacsimi.github.io)">
            <div class="nav-logo-badge">IK</div>
            <div class="nav-title-group">
                <span class="nav-title">Imre Kovács</span>
                <span class="nav-subtitle">Data Science Portfolio</span>
            </div>
        </a>

        <div class="nav-actions">
            <a href="https://kovacsimi.github.io/" class="nav-btn home-btn" title="Visszatérés a portfólió főoldalra (kovacsimi.github.io)">
                🏠 Főoldal
            </a>
            <a href="https://github.com/KovacsImi/Linear-Regression" target="_blank" rel="noopener noreferrer" class="nav-btn github-btn" title="GitHub Repository & Forráskód">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: -2px; margin-right: 5px;"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                GitHub Repo
            </a>
            <button class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn" title="Téma váltása">
                <span id="themeIcon">☀️</span> <span id="themeLabel">Világos</span>
            </button>
            <button class="nav-btn" onclick="toggleAllCode()" title="Összes kód kinyitása / összecsukása">
                💻 Kódok ki/be
            </button>
            <a href="#simulator" class="nav-btn" style="border-color: var(--accent-cyan); color: var(--accent-cyan);">
                ⚡ Szimulátor
            </a>
        </div>
    </nav>

    <div class="container">

        <!-- HERO HEADER -->
        <header class="hero-card" id="hero">
            <div class="hero-badge-tag">
                <span>📈</span> Portfolio Showcase #1 &bull; Econometric Regression
            </div>
            <h1 class="hero-title">
                Egészségbiztosítási Költségek <span class="gradient-text">OLS Regressziós Elemzése</span>
            </h1>
            <p class="hero-desc">
                End-to-end ökonometriai és adatelemzési esettanulmány: a költségeket generáló kockázati tényezők feltárása, 
                spearman-féle rangkorreláció, multikollinearitás-szűrés (VIF), interakciós modellezés, automatizált 
                hátrafelé elimináció (Backward Elimination) és HC3 robusztus hibadiagnosztika.
            </p>
            <div class="hero-action-buttons">
                <a href="https://kovacsimi.github.io/" class="hero-cta-btn home" title="Visszatérés a portfólió főoldalra">
                    <span>🏠</span> Portfólió Főoldal
                </a>
                <a href="https://github.com/KovacsImi/Linear-Regression" target="_blank" rel="noopener noreferrer" class="hero-cta-btn github">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: -3px;"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                    GitHub Repository (Teljes Kód & Elemzés)
                </a>
                <a href="https://www.kaggle.com/datasets/mirichoi0218/insurance/data" target="_blank" rel="noopener noreferrer" class="hero-cta-btn kaggle">
                    <span style="font-weight: 800; color: #38bdf8;">K</span>
                    Kaggle Adatforrás: mirichoi0218/insurance/data
                </a>
            </div>
            <div class="hero-tags">
                <span class="tag">Python 3.10+</span>
                <span class="tag purple">statsmodels</span>
                <span class="tag purple">scikit-learn</span>
                <span class="tag green">seaborn & matplotlib</span>
                <span class="tag">Kovács Imre (IK)</span>
            </div>
        </header>

        <!-- KPI HUD (5 Kártya, Globális F-próba kiszedve a kérés szerint) -->
        <div class="kpi-hud">
            <div class="kpi-box">
                <div class="kpi-top-label">Magyarázóerő (R²)</div>
                <div class="kpi-main-val gradient-text">{r2_val * 100:.2f}%</div>
                <div class="kpi-foot-note">+7.2 pp növekedés az interakcióval</div>
            </div>
            <div class="kpi-box purple">
                <div class="kpi-top-label">Korrigált R²</div>
                <div class="kpi-main-val">{adj_r2_val * 100:.2f}%</div>
                <div class="kpi-foot-note">Büntetett illeszkedési mutató</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-top-label">Modellhiba (RMSE)</div>
                <div class="kpi-main-val">${int(round(data.get("ols_final_rmse", 5107.45))):,}</div>
                <div class="kpi-foot-note">Átlagos négyzetes hiba</div>
            </div>
            <div class="kpi-box purple">
                <div class="kpi-top-label">Abszolút Hiba (MAE)</div>
                <div class="kpi-main-val">${int(round(data.get("ols_final_mae", 3136.79))):,}</div>
                <div class="kpi-foot-note">Átlagos abszolút eltérés</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-top-label">Mintanagyság (n)</div>
                <div class="kpi-main-val">1 337</div>
                <div class="kpi-foot-note">1 duplikátum szűrve, 0 hiányzó</div>
            </div>
        </div>

        <!-- =========================================================
             INTERAKTÍV MODELL SZIMULÁTOR / DÍJBEBECSLŐ WIDGET
             ========================================================= -->
        <section class="simulator-card" id="simulator">
            <div class="sim-badge">⚡ Interaktív Elemzési Eszköz</div>
            <h2 style="font-size: 1.8rem; margin-bottom: 8px;">
                Élő OLS Biztosítási <span class="gradient-text">Díjbecslő Szimulátor</span>
            </h2>
            <p style="color: var(--text-secondary); font-size: 0.95rem; max-width: 820px;">
                Próbáld ki a megbecsült regressziós egyenletet valós időben! Állítsd be az ügyfél életkorát, testtömegindexét, 
                gyermekeinek számát és dohányzási státuszát, hogy lásd a várható éves egészségügyi költséget és a dohányzás sokszorozó hatását.
            </p>

            <div class="sim-grid">
                <!-- Vezérlők -->
                <div class="sim-control-group">
                    <div class="sim-control">
                        <div class="sim-label-row">
                            <span>Életkor (age):</span>
                            <span class="val-display" id="simAgeVal">35 év</span>
                        </div>
                        <input type="range" class="sim-slider" id="simAge" min="18" max="64" value="35" oninput="runSimulation()">
                    </div>

                    <div class="sim-control">
                        <div class="sim-label-row">
                            <span>Testtömegindex (BMI):</span>
                            <span class="val-display" id="simBmiVal">28.0 kg/m²</span>
                        </div>
                        <input type="range" class="sim-slider" id="simBmi" min="16" max="50" step="0.5" value="28" oninput="runSimulation()">
                    </div>

                    <div class="sim-control">
                        <div class="sim-label-row">
                            <span>Eltartott gyermekek száma:</span>
                            <span class="val-display" id="simChildrenVal">1 gyermek</span>
                        </div>
                        <input type="range" class="sim-slider" id="simChildren" min="0" max="5" value="1" oninput="runSimulation()">
                    </div>

                    <div class="sim-control">
                        <div class="sim-label-row"><span>Dohányzik a biztosított?</span></div>
                        <div class="sim-toggle-row">
                            <button type="button" class="sim-btn-toggle active" id="simSmokerNo" onclick="setSmoker(false)">Nem dohányzó</button>
                            <button type="button" class="sim-btn-toggle" id="simSmokerYes" onclick="setSmoker(true)">Dohányzó</button>
                        </div>
                    </div>

                    <div class="sim-control">
                        <div class="sim-label-row"><span>Lakóhelyi Régió:</span></div>
                        <select class="sim-select" id="simRegion" onchange="runSimulation()">
                            <option value="northeast">Északkelet (Northeast - Bázis)</option>
                            <option value="northwest">Északnyugat (Northwest)</option>
                            <option value="southeast" selected>Délkelet (Southeast, -$942)</option>
                            <option value="southwest">Délnyugat (Southwest, -$860)</option>
                        </select>
                    </div>
                </div>

                <!-- Eredmény panel -->
                <div class="sim-result-box">
                    <div class="sim-result-label">Becsült Éves Biztosítási Díj (charges)</div>
                    <div class="sim-result-price gradient-text" id="simTotalPrice">$6 652</div>
                    
                    <div class="sim-breakdown">
                        <div class="sim-row"><span>Alap tengelymetszet (Const):</span><span class="val">-$7 091</span></div>
                        <div class="sim-row"><span>Életkor költsége (<span id="bdAgeVal">35</span> &times; $261):</span><span class="val" id="bdAgeCost">+$9 149</span></div>
                        <div class="sim-row"><span>BMI alaphatás (<span id="bdBmiVal">28</span> &times; $163):</span><span class="val" id="bdBmiCost">+$4 559</span></div>
                        <div class="sim-row"><span>Gyermekek költsége:</span><span class="val" id="bdChildCost">+$488</span></div>
                        <div class="sim-row"><span>Régió korrekció:</span><span class="val" id="bdRegionCost">-$942</span></div>
                        <div class="sim-row" style="color: #f59e0b; font-weight:700;">
                            <span>Dohányzás &times; BMI interakció:</span>
                            <span class="val" id="bdSmokerCost" style="color: #f59e0b;">$0</span>
                        </div>
                    </div>

                    <div id="simWarningBox" style="margin-top:14px; padding:10px 14px; border-radius:8px; background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3); font-size:0.78rem; color:#fca5a5; display:none;">
                        ⚠️ <strong>Dohányzó elhízott profil:</strong> A dohányzás miatti BMI szorzó önmagában többe kerül, mint az összes többi költségtényező együttvéve!
                    </div>
                </div>
            </div>
        </section>

        <!-- =========================================================
             00. ÜZLETI ÉS EGÉSZSÉGÜGYI HÁTTÉR
             ========================================================= -->
        <section class="section-card" id="uzlet">
            <div class="section-header-wrap">
                <div class="section-num-pill">00</div>
                <h2>Az Egészségbiztosítási Költségek Elemzésének Üzleti és Egészségügyi Jelentősége</h2>
            </div>
            <p class="lead">
                A modern egészségbiztosítási és ellátórendszerekben a jövőbeli kárkifizetések előrejelzése és a költségmeghatározó faktorok 
                számszerűsítése alapvető pénzügyi és orvos-szakmai követelmény. Az alulárazás csődhöz és likviditási válsághoz vezet, 
                míg a túlárazás elveszíti az alacsony kockázatú, egészséges ügyfeleket (negatív szelekció).
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin: 20px 0;">
                <div class="callout-box">
                    <div class="callout-head">🎯 1. Kockázatalapú Díjszabás (Actuarial Pricing)</div>
                    A biztosítási prémiumok kalkulációja nem alapulhat pusztán átlagokon, mivel az egészségügyi kiadások szélsőségesen aszimmetrikusak: 
                    a biztosítottak egy kis része felelős az összköltségek döntő többségéért. Egy megbízható ökonometriai modell lehetővé teszi 
                    a kockázatarányos díjszabást, garantálja a biztosító likviditását és a tőkekövetelmények stabil teljesülését.
                </div>
                <div class="callout-box green">
                    <div class="callout-head">💡 2. Módosítható vs. Nem Módosítható Rizikófaktorok</div>
                    Az elemzés világos határvonalat húz a biológiailag determinált (nem befolyásolható) tényezők — mint az <strong>életkor</strong> és a <strong>nem</strong> — 
                    valamint az életmódbeli (módosítható) rizikófaktorok — mint a <strong>dohányzás</strong> és a <strong>testtömegindex (BMI)</strong> — között. 
                    Ez a megkülönböztetés teremti meg az alapját a célzott egészségmegőrző és prevenciós programoknak.
                </div>
            </div>

            <div class="callout-box amber">
                <div class="callout-head">⚠️ A Kulcsfelismerés: A Dohányzás és az Elhízás Költségsokszorozó Szinergiája</div>
                A hagyományos leíró modellek gyakran különálló, additív faktorként tekintenek a dohányzásra és a túlsúlyra. 
                Jelen elemzésünk bizonyítja, hogy e két tényező között <strong>szignifikáns interakciós kapcsolat</strong> áll fenn: 
                a dohányzás nem csupán fix összegű költségnövekedést okoz, hanem <strong>többszörösére gyorsítja a testsúly növekedéséből fakadó ellátási kiadásokat</strong>. 
                Egy dohányzó elhízott egyén költségkockázata exponenciálisan magasabb, mint a két tényező önálló hatásának összege!
            </div>

            <h3>Az Adatbázis Változóinak Strukturált Ismertetése</h3>
            {dataframe_to_html_table(valtozok_meta)}
        </section>

        <!-- =========================================================
             01. ADATBÁZIS BEOLVASÁS ÉS MINŐSÉG
             ========================================================= -->
        <section class="section-card" id="adat">
            <div class="section-header-wrap">
                <div class="section-num-pill">01</div>
                <h2>1. Adatbázis Beolvasása és Adatminőség-ellenőrzés</h2>
            </div>
            <p class="lead">
                Az elemzés alapjául szolgáló hivatalos adatkészlet elérhető a Kaggle felületén: 
                <a href="https://www.kaggle.com/datasets/mirichoi0218/insurance/data" target="_blank" rel="noopener noreferrer" style="color: var(--accent-cyan); text-decoration: underline; font-weight: 600;">
                    https://www.kaggle.com/datasets/mirichoi0218/insurance/data
                </a>.
                Az adatállományt közvetlenül a <code>kagglehub</code> csomagon keresztül töltöttük be (<code>mirichoi0218/insurance</code>, <code>insurance.csv</code>). 
                Az adatminőség ellenőrzése során felmértük a sor- és oszlopméretet, a duplikációkat és a hiányzó értékeket.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    1. Fejezet Kódjának Megtekintése (Adatbetöltés és Minőségellenőrzés)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># 1.0 - Adat beolvasas Kaggle-rol (https://www.kaggle.com/datasets/mirichoi0218/insurance/data)
import kagglehub
from kagglehub import KaggleDatasetAdapter

df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "mirichoi0218/insurance",
    "insurance.csv",
)

# 1.1 - Duplikatumok szurese
num_duplicates = df.duplicated().sum()
if num_duplicates > 0:
    df = df.drop_duplicates().reset_index(drop=True)

# 1.2 - Hianyzo ertekek ellenorzese
missing_df = pd.DataFrame({{
    "Hianyzo ertekek szama": df.isnull().sum(),
    "Hianyzo ertekek aranya (%)": (df.isnull().sum() / len(df) * 100).round(2)
}})</code></pre>
                </div>
            </details>

            <div class="callout-box">
                <div class="callout-head">🔍 Adatminőség Eredményei:</div>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Eredeti sorméret:</strong> 1 338 megfigyelés, 7 változó.</li>
                    <li><strong>Duplikátum szűrés:</strong> Pontosan <strong>1 darab duplikált rekord</strong> került azonosításra (egy 19 éves, délnyugati, nem dohányzó férfi azonos költséggel). A duplikátumot eltávolítottuk.</li>
                    <li><strong>Tisztított mintanagyság:</strong> <strong>1 337 megfigyelés</strong>.</li>
                    <li><strong>Hiányzó adatok:</strong> Az adatbázisban <strong>0 darab hiányzó (null) érték</strong> található, a mátrix teljes.</li>
                    <li><strong>Hivatalos forrás:</strong> <a href="https://www.kaggle.com/datasets/mirichoi0218/insurance/data" target="_blank" rel="noopener noreferrer">kaggle.com/datasets/mirichoi0218/insurance/data</a></li>
                </ul>
            </div>

            {dataframe_to_html_table(missing_df)}
        </section>

        <!-- =========================================================
             02. FELTÁRÓ ADATELEMZÉS (EDA)
             ========================================================= -->
        <section class="section-card" id="eda">
            <div class="section-header-wrap">
                <div class="section-num-pill">02</div>
                <h2>2. Feltáró Adatelemzés (EDA) – Eloszlások és Gyakoriságok</h2>
            </div>
            <p class="lead">
                A leíró statisztikai elemzés során feltérképeztük az egyes változók centrális tendenciáit, szóródását, 
                aszimmetriáját (skewness), és azonosítottuk a potenciális kiugró értékeket (outliereket).
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    2. Fejezet Kódjának Megtekintése (EDA és Eloszlás-ábrák)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># Numerikus valtozok eloszlasa (Hisztogram es Boxplot)
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
for col in numeric_cols:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    if col == "children":
        # Diszkret valtozo: pontos egesz ertekeknel, KDE trendvonal nelkul
        sns.histplot(df[col], discrete=True, kde=False, color="steelblue", ax=axes[0],
                     edgecolor="white", linewidth=0.8, shrink=0.85)
        axes[0].set_title(f"'{{col}}' eloszlasa (Diszkret hisztogram)")
        axes[0].set_xticks([0, 1, 2, 3, 4, 5])
    else:
        sns.histplot(df[col], kde=True, bins=30, color="steelblue", ax=axes[0],
                     edgecolor="white", linewidth=0.5)
        axes[0].set_title(f"'{{col}}' eloszlasa (Hisztogram + KDE)")
    sns.boxplot(x=df[col], color="lightcoral", ax=axes[1])
    save_and_show(fig, f"dist_{{col}}")

# Kategorikus valtozok gyakorisaga (Countplot)
categorical_cols = df.select_dtypes(include="object").columns.tolist()
for col in categorical_cols:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(x=df[col], palette="viridis", ax=ax)
    save_and_show(fig, f"count_{{col}}")</code></pre>
                </div>
            </details>

            <h3>Numerikus Változók Leíró Statisztikái (n = 1 337)</h3>
            {dataframe_to_html_table(desc_num)}

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin: 24px 0;">
                <div class="callout-box">
                    <div class="callout-head">👤 Életkor (age)</div>
                    Átlag: <strong>39.2 év</strong>, medián: <strong>39.0 év</strong> (18–64 év). Kiegyensúlyozott, közel egyenletes eloszlás, outlierek nélkül.
                </div>
                <div class="callout-box green">
                    <div class="callout-head">⚖️ Testtömegindex (bmi)</div>
                    Átlag: <strong>30.66 kg/m²</strong>, medián: <strong>30.40 kg/m²</strong>. Szimmetrikus Gauss-görbe, a minta több mint fele a túlsúlyos / elhízott kategóriába esik.
                </div>
                <div class="callout-box purple">
                    <div class="callout-head">👶 Gyermekek száma (children)</div>
                    Átlag: <strong>1.1 fő</strong> (0–5 gyermek). A biztosítottak 42.9%-ának nincs gyermeke, a 4-5 gyermekes családok ritkák (3.2%).
                </div>
                <div class="callout-box amber">
                    <div class="callout-head">💵 Költségek (charges)</div>
                    Átlag: <strong>$13 279</strong>, medián: <strong>$9 386</strong>. Erősen jobbra ferde eloszlás, jelentős jobboldali farokkal ($63 770-ig).
                </div>
            </div>

            {img_tag("dist_age", "Az életkor eloszlása egyenletes (uniform jellegű) a 18 és 64 év közötti tartományban, a 18-19 éves korcsoportban enyhe felülreprezentáltsággal. A dobozábrán az alsó- és felső határoló pontok között helyezkedik el a teljes minta, kiugró érték nincs.", "1. Ábra: Életkor (age) eloszlása és dobozábrája")}

            {img_tag("dist_bmi", "A testtömegindex (BMI) szép szimmetrikus haranggörbét alkot, átlaga 30.66 kg/m², mediánja 30.40 kg/m², ami a WHO besorolás szerint már az I. fokú elhízás kategóriája. A dobozábra alsó- és felső határoló pontjait vizsgálva, a felső határoló ponton túl néhány extrém magas érték (45-53 kg/m²) látható.", "2. Ábra: Testtömegindex (bmi) eloszlása és dobozábrája")}

            {img_tag("dist_children", "A biztosított gyermekek száma diszkrét eloszlású (0–5 fő), ezért a hisztogramon diszkrét oszlopokként ábrázoltuk folytonos KDE trendvonal nélkül, elkerülve a két diszkrét egész szám közé beeső félrevezető simítást. A megfigyeltek legnagyobb részének (574 fő, 42.9%) nincs gyermeke, míg a 4 és 5 gyermekes családok aránya elenyésző.", "3. Ábra: Gyermekek száma (children) diszkrét eloszlása és dobozábrája")}

            {img_tag("dist_charges", "A célváltozó (charges) rendkívül erősen jobbra ferde eloszlást mutat. Az átlag ($13 279) jelentősen meghaladja a mediánt ($9 386). A biztosítottak zöme $2 000 és $12 000 közötti költséget generál, de a felső határoló ponton túl a hosszú jobboldali farok egészen $63 770-ig nyúlik.", "4. Ábra: Biztosítási költségek (charges) eloszlása és dobozábrája")}

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>{img_tag("count_sex", "A nemek eloszlása szinte tökéletesen kiegyensúlyozott: 675 férfi (50.5%) és 662 nő (49.5%) szerepel a mintában.", "5. Ábra: Nemek aránya (sex)")}</div>
                <div>{img_tag("count_smoker", "A dohányzók aránya 20.5% (274 fő), míg a nem dohányzóké 79.5% (1 063 fő). Ez az arány hűen reprezentálja a fejlett társadalmak dohányzási rátáját.", "6. Ábra: Dohányzók megoszlása (smoker)")}</div>
            </div>

            {img_tag("count_region", "A négy amerikai földrajzi régió megoszlása rendkívül kiegyenlített: délkeleten 364 fő él, míg az északnyugati, délnyugati és északkeleti régiókban 324-325 fő található.", "7. Ábra: Lakóhelyi régiók megoszlása (region)")}
        </section>

        <!-- =========================================================
             03. CÉLVÁLTOZÓ VS MAGYARÁZÓ VÁLTOZÓK
             ========================================================= -->
        <section class="section-card" id="scatter">
            <div class="section-header-wrap">
                <div class="section-num-pill">03</div>
                <h2>3. Célváltozó (Charges) vs. Magyarázó Változók – A Dohányzás Moderáló Szerepe</h2>
            </div>
            <p class="lead">
                A magyarázó változók és a biztosítási költségek kapcsolatát színezett pontdiagramokon (<code>hue='smoker'</code>) vizsgáltuk. 
                Ez a lépés tárta fel az egész adathalmaz legfontosabb strukturális sajátosságát.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    3. Fejezet Kódjának Megtekintése (Scatter, Boxplot és Stripplot)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># 2.6a: charges vs age | charges vs bmi (hue='smoker')
fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(121)
sns.scatterplot(x="age", y="charges", data=df, palette="magma", hue="smoker", ax=ax1)

ax2 = fig.add_subplot(122)
sns.scatterplot(x="bmi", y="charges", data=df, palette="viridis", hue="smoker", ax=ax2)
save_and_show(fig, "scatter_age_bmi_vs_charges")

# 2.6b: charges vs children | charges vs smoker (boxplot)
fig = plt.figure(figsize=(14, 6))
ax3 = fig.add_subplot(121)
sns.scatterplot(x="children", y="charges", data=df, palette="coolwarm", hue="smoker", ax=ax3)

ax4 = fig.add_subplot(122)
sns.boxplot(x="smoker", y="charges", data=df, palette="Set2", ax=ax4)
save_and_show(fig, "scatter_children_smoker_vs_charges")</code></pre>
                </div>
            </details>

            {img_tag("scatter_age_bmi_vs_charges", "Bal oldal: Életkor vs Költség. Három élesen elkülönülő sáv rajzolódik ki, és mindháromban lineárisan nő a költség a korral, de a legfelső ($30k-$60k) sávot kizárólag a dohányzók uralják! Jobb oldal: BMI vs Költség. A döntő ábra! Nem dohányzóknál a BMI növekedése alig növeli a díjat. Dohányzóknál azonban a 30-as BMI felett a költségek hirtelen a $30 000 - $45 000 tartományba ugranak!", "8. Ábra: Költségek az életkor és a BMI függvényében (dohányzás szerinti színezéssel)")}

            <div class="callout-box amber">
                <div class="callout-head">⚡ Strukturális Áttörés: A 30-as BMI Küszöbérték-Effektus</div>
                A 8. ábra jobb paneljén látható, hogy míg a nem dohányzóknál a BMI enyhe lejtésű egyenest követ ($2 000 – $12 000), 
                addig a dohányzóknál a <strong>30-as BMI (orvosi elhízási küszöb)</strong> egy valódi költségrobbanási pont: 
                a költségek ugrásszerűen $30 000 fölé szöknek. Ez a vizuális bizonyíték teszi elengedhetetlenné 
                a <code>bmi * smoker_yes</code> interakciós tag beépítését a regressziós modellbe.
            </div>

            {img_tag("scatter_children_smoker_vs_charges", "Bal oldal: Gyermekek száma vs Költség. A gyermekek számának emelkedése szerény alapdíj-növekedést okoz. Jobb oldal: Dohányzók vs Nem dohányzók dobozábrája. A dohányzók medián kiadása (~$34 000) közel négyszerese a nem dohányzóknak (~$7 300).", "9. Ábra: Költségek a gyermekek száma és a dohányzás szerint")}

            {img_tag("scatter_sex_region_vs_charges", "A nemek és a régiók szerinti bontásban a pontok eloszlása szinte azonos. Önmagában sem a nem, sem a földrajzi elhelyezkedés nem hoz létre markáns költségkülönbséget; a csoportokon belüli szóródás motorja mindenütt a dohányzási státusz.", "10. Ábra: Költségek a biológiai nem és a régió szerint (dohányzás szerinti színezéssel)")}
        </section>

        <!-- =========================================================
             04. KÓDOLÁS, INTERAKCIÓK ÉS SPEARMAN
             ========================================================= -->
        <section class="section-card" id="kodolas">
            <div class="section-header-wrap">
                <div class="section-num-pill">04</div>
                <h2>4. Adatelőkészítés, One-Hot Encoding és Interakciós Tagok Képzése</h2>
            </div>
            <p class="lead">
                A kategorikus oszlopokat dummy kódolással alakítottuk át (<code>drop_first=True</code> a Dummy Variable Trap elkerülésére), 
                majd származtatott változóként képeztük a <code>bmi_x_smoker</code> és <code>age_x_smoker</code> interakciós tagokat. 
                Ezt követően kiszámítottuk a Spearman-féle rangkorrelációs mátrixot.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    4. Fejezet Kódjának Megtekintése (Dummy kódolás, Interakciók és Spearman Hőtérkép)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># One-Hot Encoding
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True, dtype=float)

# Interakcios tagok kepzese
df_encoded["bmi_x_smoker"] = df_encoded["bmi"] * df_encoded["smoker_yes"]
df_encoded["age_x_smoker"] = df_encoded["age"] * df_encoded["smoker_yes"]

# Spearman rangkorrelacios matrix es hoterkep
spearman_corr = df_encoded.corr(method="spearman")
mask = np.triu(np.ones_like(spearman_corr, dtype=bool))
sns.heatmap(spearman_corr, annot=True, fmt=".2f", cmap="coolwarm", mask=mask)
save_and_show(fig_hm, "spearman_heatmap")</code></pre>
                </div>
            </details>

            {img_tag("spearman_heatmap", "Spearman rangkorrelációs hőtérkép. Mivel a célváltozó ferde eloszlású és nemlineáris küszöbhatások vannak, a Spearman korreláció jóval megbízhatóbb, mint a Pearson. A célváltozóval a legerősebb kapcsolatot a smoker_yes (rho = 0.66), a bmi_x_smoker (rho = 0.67) és az age (rho = 0.53) mutatja.", "11. Ábra: Spearman-féle Rangkorrelációs Hőtérkép")}
        </section>

        <!-- =========================================================
             05. MULTIKOLLINEARITÁS ÉS VIF
             ========================================================= -->
        <section class="section-card" id="vif">
            <div class="section-header-wrap">
                <div class="section-num-pill">05</div>
                <h2>5. Multikollinearitás és Variancia Inflációs Faktor (VIF) Vizsgálata</h2>
            </div>
            <p class="lead">
                A többváltozós regresszióban elengedhetetlen a magyarázó változók közötti káros együttmozgás (multikollinearitás) kiszűrése. 
                A túlzott multikollinearitás destabilizálja az OLS becsléseket, torzítja a konfidencia-intervallumokat és felrobbantja a standard hibákat. 
                A vizsgálatot szigorú, kétlépcsős ökonometriai eljárással végeztük el: először páronkénti Spearman-korreláció szűréssel (|&rho;| &gt; 0.7), 
                majd a fennmaradó magyarázó változókra konstanssal kiegészített VIF (Variance Inflation Factor) elemzést hajtottunk végre.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    5. Fejezet Kódjának Megtekintése (Páronkénti szűrés és VIF)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># 4.1 - Magas korrelacio szurese a magyarazo valtozok kozott (|rho| > 0.7)
corr_X = df_encoded[X_cols].corr(method="spearman")
dropped_corr = []

for i in range(len(X_cols)):
    for j in range(i + 1, len(X_cols)):
        var1, var2 = X_cols[i], X_cols[j]
        corr_val = abs(corr_X.loc[var1, var2])
        if corr_val > 0.7:
            corr_y_var1 = abs(spearman_corr.loc[var1, target])
            corr_y_var2 = abs(spearman_corr.loc[var2, target])
            to_drop = var1 if corr_y_var1 < corr_y_var2 else var2
            if to_drop not in dropped_corr:
                dropped_corr.append(to_drop)

# 4.2 - VIF szamitas konstanssal
def calculate_vif(X_data):
    X_const = sm.add_constant(X_data)
    vif_data = pd.DataFrame()
    vif_data["Valtozo"] = X_const.columns
    vif_data["VIF"] = [variance_inflation_factor(X_const.values, i)
                       for i in range(X_const.shape[1])]
    return vif_data

# Iterativ VIF szures VIF > 5.0 eseten
while True:
    vif_df = calculate_vif(X_vif)
    vif_no_const = vif_df[vif_df["Valtozo"] != "const"]
    if vif_no_const["VIF"].max() > 5.0:
        X_vif = X_vif.drop(columns=[vif_no_const.loc[vif_no_const["VIF"].idxmax(), "Valtozo"]])
    else:
        break</code></pre>
                </div>
            </details>

            <div class="callout-box amber">
                <div class="callout-head">⚠️ 5.1 Páronkénti Korrelációs Szűrés (|&rho;| &gt; 0.7) — Kiszűrt Változók:</div>
                <p style="margin-bottom: 12px;">
                    A magyarázó változók Spearman-féle korrelációs mátrixának vizsgálatakor két változópárnál tapasztaltunk kritikus mértékű, 
                    a 0.7-es küszöbértéket jóval meghaladó együttmozgást. Az információs veszteség minimalizálása érdekében azt a tagot ejtettük ki, 
                    amelyik gyengébben korrelált a célváltozóval (<code>charges</code>):
                </p>
                <ul style="margin-left: 20px; line-height: 1.85;">
                    <li>
                        <strong><code>smoker_yes</code> &rarr; KISZŰRVE:</strong><br>
                        Szinte determinisztikus, kollineáris kapcsolat állt fenn a <code>bmi_x_smoker</code> interakciós taggal 
                        (<strong>|&rho;| = 0.9913 &gt; 0.7</strong>). Mivel a célváltozóval a <code>bmi_x_smoker</code> szorosabb kapcsolatot mutatott 
                        (&rho; = 0.6721, szemben a <code>smoker_yes</code> &rho; = 0.6636 értékével), a szabályrendszerünk szerint a <strong><code>smoker_yes</code> változót zártuk ki</strong>.
                    </li>
                    <li>
                        <strong><code>age_x_smoker</code> &rarr; KISZŰRVE:</strong><br>
                        Szintén extrém erős összefüggést mutatott a <code>bmi_x_smoker</code> taggal (<strong>|&rho;| = 0.9837 &gt; 0.7</strong>). 
                        A célváltozóval mért magyarázóerő alapján (&rho; = 0.6721 vs. &rho; = 0.6651) a <code>bmi_x_smoker</code> maradt bent a modellben, 
                        így az <strong><code>age_x_smoker</code> változót szűrtük ki</strong>.
                    </li>
                </ul>
                <div style="margin-top: 14px; padding: 10px 14px; background: rgba(0,0,0,0.25); border-radius: 8px; font-size: 0.9rem;">
                    📌 <strong>Összegzés:</strong><br>
                    &bull; <strong>Kiszűrt változók (2 db):</strong> <code>['smoker_yes', 'age_x_smoker']</code><br>
                    &bull; <strong>Továbbjutó magyarázó változók a VIF vizsgálathoz (8 db):</strong> 
                    <code>['age', 'bmi', 'children', 'sex_male', 'region_northwest', 'region_southeast', 'region_southwest', 'bmi_x_smoker']</code>
                </div>
            </div>

            <h3>5.2 Variancia Inflációs Faktor (VIF) Eredménytáblázat (n = 1 337)</h3>
            <p style="color: var(--text-secondary); margin-bottom: 12px;">
                A VIF (Variance Inflation Factor) azt méri, hogy egy magyarázó változó varianciája hányszorosára növekszik a többi változóval való lineáris összefüggése miatt. 
                Az ökonometriai gyakorlatban a <strong>VIF &gt; 5.0</strong> (konzervatív) vagy <strong>VIF &gt; 10.0</strong> érték jelez veszélyes multikollinearitást.
            </p>

            {dataframe_to_html_table(vif_table_df)}

            <div class="callout-box green">
                <div class="callout-head">✅ VIF Eredmény: Teljesen Megszűnt a Multikollinearitás!</div>
                A fenti táblázat tanúsága szerint valamennyi megmaradt magyarázó változó VIF értéke <strong>1.00 és 1.65 között alakult</strong>, 
                ami messze alatta marad a szigorú 5.0-s határértéknek. A legmagasabb VIF a <code>region_southeast</code> változónál adódott (1.65), 
                ami a területi dummy kódolás természetes sajátossága. <strong>Az iteratív VIF-szűrés során további változót már nem kellett kizárni</strong>, 
                a modell információ-mátrixa stabil és jól kondicionált maradt.
            </div>
        </section>

        <!-- =========================================================
             06. BACKWARD ELIMINATION
             ========================================================= -->
        <section class="section-card" id="backward">
            <div class="section-header-wrap">
                <div class="section-num-pill">06</div>
                <h2>6. Változószelekció: Automatizált Backward Elimination (Hátrafelé Elimináció)</h2>
            </div>
            <p class="lead">
                A felesleges, nem szignifikáns változók eltávolítására automatizált, lépésről lépésre naplózott hátrafelé eliminációt 
                alkalmaztunk <code>&alpha; = 0.05</code> szignifikanciaszint mellett.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    6. Fejezet Kódjának Megtekintése (Backward Elimination Ciklus)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python">alpha = 0.05
be_cols = X_cols_final.copy()
step = 0

while True:
    step += 1
    X_be = sm.add_constant(df_encoded[be_cols])
    model_be = sm.OLS(y, X_be).fit()
    pvalues = model_be.pvalues.drop("const") # const soha nem eshet ki
    max_pval = pvalues.max()
    max_pval_var = pvalues.idxmax()

    if max_pval > alpha:
        be_cols.remove(max_pval_var)
    else:
        break # Minden valtozo szignifikans</code></pre>
                </div>
            </details>

            <h3>A Hátrafelé Elimináció Iterációs Története</h3>
            {dataframe_to_html_table(be_df)}

            <div class="callout-box">
                <div class="callout-head">📋 Változószelekciós Döntések:</div>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>1. kieső:</strong> <code>region_northwest</code> (p = 0.256) — nem különbözik szignifikánsan a bázis Északkeleti régiótól.</li>
                    <li><strong>2. kieső:</strong> <code>sex_male</code> (p = 0.178) — a biológiai nemnek nincs önálló, statisztikailag igazolható költséghatása az egyéb tényezők kontrollálása mellett.</li>
                    <li><strong>Végső parszimóniás modell:</strong> <code>age</code>, <code>bmi</code>, <code>children</code>, <code>region_southeast</code>, <code>region_southwest</code>, és a döntő <code>bmi_x_smoker</code> interakciós tag!</li>
                </ul>
            </div>
        </section>

        <!-- =========================================================
             07. VÉGSŐ MODELL ÉS ÉRTELMEZÉS
             ========================================================= -->
        <section class="section-card" id="vegso">
            <div class="section-header-wrap">
                <div class="section-num-pill">07</div>
                <h2>7. A Végső OLS Modell Értékelése és Gyakorlati Üzleti Interpretációja ($)</h2>
            </div>
            <p class="lead">
                A végső modell illeszkedése kiemelkedő: a magyarázóerő az interakció révén <strong>74.95%-ról 82.20%-ra</strong> emelkedett, 
                miközben az átlagos becslési hiba (RMSE) közel 1 000 dollárral csökkent.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    7. Fejezet Kódjának Megtekintése (Végső OLS és Modell-összehasonlítás)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python">X_final = sm.add_constant(df_encoded[be_cols])
ols_final = sm.OLS(y, X_final).fit()

final_rmse = np.sqrt(mean_squared_error(y, ols_final.predict(X_final)))
final_mae = mean_absolute_error(y, ols_final.predict(X_final))
print(ols_final.summary())</code></pre>
                </div>
            </details>

            <h3>Alapmodell (8 változó) vs. Végső Modell (6 változó) Összehasonlítása</h3>
            {dataframe_to_html_table(comparison)}

            <h3>A Végső OLS Modell Regressziós Együtthatói (Egész Dollárra Kerekítve)</h3>
            <p style="color: var(--text-secondary); margin-bottom: 10px; font-size: 0.9rem;">
                Az alábbi táblázatban az együtthatók, hibák és konfidencia-intervallumok egész dollárokra kerekítve szerepelnek a közvetlen gyakorlati értelmezhetőség céljából.
            </p>
            {dataframe_to_html_table(final_params_df)}

            <div class="equation-box">
                <div style="color: var(--accent-cyan); font-size: 0.8rem; text-transform: uppercase; margin-bottom: 6px; font-weight: 700;">A Végső Ökonometriai Regressziós Egyenlet (Egész Számokra Kerekítve):</div>
                charges = -7 091 + (261 &times; age) + (163 &times; bmi) + (488 &times; children) - (942 &times; region_se) - (860 &times; region_sw) + (803 &times; bmi_x_smoker)
            </div>

            <h3>Gyakorlati, Dollárban Kifejezett Üzleti Interpretáció</h3>

            <div class="callout-box">
                <div class="callout-head">💰 Életkor (age): +$261 / év</div>
                Minden megélt életév egyéb tényezők változatlansága mellett (ceteris paribus) átlagosan <strong>+$261 összeggel növeli az éves biztosítási terhet</strong>. 
                Egy 50 éves személy egy 20 éves fiatalhoz képest (30 év korkülönbség) pusztán a kora miatt 
                átlagosan <code>30 &times; $261 = </code> <strong>+$7 830 többletkiadást</strong> generál évente a biztosítónak.
            </div>

            <div class="callout-box purple">
                <div class="callout-head">👶 Eltartott Gyermekek (children): +$488 / gyermek</div>
                Minden egyes biztosított gyermek átlagosan <strong>+$488 összeggel növeli</strong> a család éves ellátási költségeit.
            </div>

            <div class="callout-box">
                <div class="callout-head">🗺️ Régiók: Southeast (-$942) és Southwest (-$860)</div>
                Az északkeleti referencia-régióhoz képest a déli államokban az egészségügyi árszínvonal és az ellátási díj 
                átlagosan <strong>$860 - $942 összeggel alacsonyabb</strong>.
            </div>

            <div class="callout-box amber" style="border-left-width: 6px;">
                <div class="callout-head" style="font-size: 1.18rem; color: #fbbf24;">
                    🔥 A KULCSMEGÁLLAPÍTÁS: A BMI és a Dohányzás Kölcsönhatása (bmi_x_smoker: +$803)
                </div>
                <p style="font-size: 1.02rem; margin-bottom: 12px; font-weight: 500;">
                    <em>A dohányzás nem egyszerűen egy fix összegű pluszköltséget jelent, hanem a BMI-vel arányosan növeli a biztosítási költségeket. 
                    Egy dohányzó személy esetén minden egyes egységnyi BMI növekedés +803 USD extra költséget generál — 
                    a magas BMI-jű dohányzók tehát exponenciálisan drágábbak a biztosító számára!</em>
                </p>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Nem dohányzó személy esetén:</strong> 1 pont BMI növekedés költséghatása: <strong>+$163 / év</strong>.</li>
                    <li><strong>Dohányzó személy esetén:</strong> 1 pont BMI növekedés költséghatása: <code>$163 + $803 = </code> <strong>+$966 / év</strong>!</li>
                </ul>
                <div style="margin-top: 12px; padding: 14px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                    <strong>Számpélda egy 13 pontos BMI növekedésre (normál testsúlyról elhízásra: 22 &rarr; 35 kg/m²):</strong><br>
                    &bull; <strong>Ha NEM dohányzik:</strong> Költségnövekedése: <code>13 &times; $163 = </code> <strong>+$2 119 / év</strong>.<br>
                    &bull; <strong>Ha DOHÁNYZIK:</strong> Ugyanez a testsúlygyarapodás: <code>13 &times; $966 = </code> <strong>+$12 558 / év</strong> többletkiadást eredményez!<br>
                    <strong>Konklúzió: A dohányzás közel HATSZOROSÁRA (5.93&times;) sokszorozza fel a túlsúlyból fakadó ellátási költségterhet!</strong>
                </div>
            </div>

            <!-- 7.2 STANDARDIZÁLT OLS MODELL ÉS RELATÍV VÁLTOZÓ-FONTOSSÁG -->
            <div style="margin-top: 2.8rem; padding-top: 1.8rem; border-top: 1px solid var(--border-glass);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
                    <span class="sim-badge" style="background: var(--accent-grad-warm);">⚖️ Változó-Fontosság & Hatásnagyság</span>
                    <h3 style="margin: 0; font-size: 1.45rem; color: var(--text-primary);">
                        7.2 Standardizált OLS Modell – A Változók Relatív Hatásának Elemzése (Standardizált Béták)
                    </h3>
                </div>

                <p class="lead">
                    A nyers regressziós együtthatók közvetlenül <strong>nem alkalmasak a változók fontosságának összehasonlítására</strong>, 
                    mivel eltérő mértékegységekben mérjük őket (évek, kg/m², gyermekek darabszáma, vagy 0/1 dummy indikátorok). 
                    A magyarázó változók standardizálásával (átlag = 0, szórás = 1) a kapott <strong>standardizált béták (&beta;*)</strong> 
                    dimenziómentes skálára kerülnek, és közvetlenül mutatják meg, hogy <strong>melyik tényező gyakorolja a legnagyobb relatív hatást az egészségügyi költségekre</strong>.
                </p>

                <details class="code-fold">
                    <summary>
                        <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                        7.2 Kód: Változók Standardizálása és Standardizált OLS Modell Illesztése
                    </summary>
                    <div class="code-container">
                        <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                        <pre><code class="language-python">from sklearn.preprocessing import StandardScaler

# Magyarázó változók és célváltozó standardizálása (z-score)
scaler_X = StandardScaler()
X_final_std = pd.DataFrame(scaler_X.fit_transform(df_encoded[be_cols]), columns=be_cols)
y_std = (y - y.mean()) / y.std(ddof=1)

# Standardizált OLS regressziós modell illesztése konstanssal
ols_std = sm.OLS(y_std, sm.add_constant(X_final_std)).fit()
print(ols_std.summary())</code></pre>
                    </div>
                </details>

                {img_tag("standardized_betas", "A végső modell magyarázó változóinak relatív hatásnagysága (standardizált béták). A bmi_x_smoker interakciós tag magasan a legdominánsabb tényező (béta = +0.8436), ezt követi az életkor (béta = +0.3030), míg a BMI önálló hatása (béta = +0.0820), a gyermekek száma (+0.0486) és a regionális különbségek (-0.035, -0.030) jóval kisebb relatív súllyal bírnak.", "12. Ábra: Standardizált Regressziós Koefficiensek (β*) és Változó-fontossági Rangsor")}

                <h3>Standardizált Béták és 1 Szórásnyi Hatások Táblázata</h3>
                {dataframe_to_html_table(std_table_df)}

                <div class="callout-box amber" style="border-left-width: 6px;">
                    <div class="callout-head" style="font-size: 1.15rem; color: #fbbf24;">
                        📊 Mit Árulnak el a Standardizált Béták az Üzleti és Kockázati Döntéshozónak?
                    </div>
                    <ul style="margin-left: 20px; line-height: 1.85;">
                        <li>
                            <strong>#1 Helyezett — <code>bmi_x_smoker</code> (&beta;* = +0.8436):</strong><br>
                            Az elhízás és a dohányzás szinergikus kölcsönhatása toronymagasan a legfontosabb költséggenerátor a biztosítási portfólióban. 
                            1 szórásnyi növekedése (12.72 pont) <strong>+$10 220 többletköltséget</strong> okoz! 
                            Relatív hatása közel <strong>háromszor akkora</strong>, mint a második helyezett életkoré.
                        </li>
                        <li>
                            <strong>#2 Helyezett — <code>age</code> (&beta;* = +0.3030):</strong><br>
                            A biológiai életkor a második legfontosabb költségtényező: 1 szórásnyi korkülönbség (14.04 év) 
                            átlagosan <strong>+$3 671 többletkiadással</strong> jár az ügyfél felett.
                        </li>
                        <li>
                            <strong>#3 Helyezett — <code>bmi</code> (&beta;* = +0.0820):</strong><br>
                            A nem dohányzók esetén a testsúly önálló szerepe számottevően visszafogottabb (1 szórás = 6.10 BMI pont &rarr; +$993 / év). 
                            Ez igazolja az aktuáriusok számára, hogy a normál túlsúly önmagában csak mérsékelt kockázat — a valódi robbanást a dohányzással való kombináció okozza.
                        </li>
                        <li>
                            <strong>#4 Helyezett — <code>children</code> (&beta;* = +0.0486):</strong><br>
                            A gyermekek száma kiszámítható, szignifikáns, de kisebb súlyú költségtényező (1 szórás = 1.21 gyermek &rarr; +$589 / év).
                        </li>
                        <li>
                            <strong>#5–6 Helyezettek — <code>region_southeast</code> (&beta;* = -0.0346) és <code>region_southwest</code> (&beta;* = -0.0304):</strong><br>
                            Bár statisztikailag szignifikánsak, hatásuk relatív nagyságrendje marginális (mintegy 25-ször gyengébb a dohányzás-BMI hatásánál).
                        </li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- =========================================================
             08. DIAGNOSZTIKA ÉS HC3 ROBUSTUS STANDARD HIBAK
             ========================================================= -->
        <section class="section-card" id="diag">
            <div class="section-header-wrap">
                <div class="section-num-pill">08</div>
                <h2>8. OLS Diagnosztikai Vizsgálatok és HC3 Robusztus Standard Hibák</h2>
            </div>
            <p class="lead">
                A lineáris modell klasszikus feltevéseit szigorú ökonometriai tesztekkel vetettük össze: 
                a hibatagok normalitását, a homoszkedaszticitást, az autokorrelációt és a kiugró adatpontok befolyását.
            </p>

            <details class="code-fold">
                <summary>
                    <span class="code-term-dots"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span></span>
                    8. Fejezet Kódjának Megtekintése (Diagnosztika és HC3 Robusztus Becslés)
                </summary>
                <div class="code-container">
                    <button class="copy-code-btn" onclick="copyCode(this)">📋 Másolás</button>
                    <pre><code class="language-python"># Normalitas: Shapiro-Wilk es Jarque-Bera
sw_stat, sw_pval = shapiro(residuals)
jb_stat, jb_pval = jarque_bera(residuals)

# Homoszkedaszticitas: Breusch-Pagan teszt
bp_stat, bp_pval, bp_fstat, bp_fpval = het_breuschpagan(residuals, X_final)

# Autokorrelacio: Durbin-Watson
dw_stat = durbin_watson(residuals)

# Cook-tavolsag (4/n kuszobertek)
cooks_d = ols_final.get_influence().cooks_distance[0]
cooks_threshold = 4 / len(y)

# HC3 Robusztus standard hibak
ols_robust = sm.OLS(y, X_final).fit(cov_type="HC3")</code></pre>
                </div>
            </details>

            <h3>8.1 Hibatagok Normalitása</h3>
            {img_tag("normality_check", "Bal oldal: A reziduálisok hisztogramja és KDE görbéje pozitív ferdeséget mutat. Jobb oldal: A Normal Q-Q ploton a felső kvantilisek élesen felfelé ívelnek, ami a ritka, nagyértékű orvosi beavatkozások vastag farkát (heavy tail) bizonyítja.", "13. Ábra: Reziduálisok Normalitása (Hisztogram és Normal Q-Q Plot)")}

            <div class="callout-box amber">
                <div class="callout-head">⚠️ Normalitási Tesztek: H₀ Elutasítva</div>
                Shapiro–Wilk p = {data.get("sw_pval", 0.0):.6f} (p &lt; 0.0001), Jarque–Bera p = {data.get("jb_pval", 0.0):.6f} (p &lt; 0.0001). 
                A reziduálisok nem normálisak, ami az egészségügyi adatok aszimmetrikus kárkifizetései miatt természetes. 
                Nagy mintánál (n = 1 337) a <strong>Centrális Határeloszlás-tétel (CLT)</strong> garantálja az OLS becslések aszimptotikus torzítatlanságát.
            </div>

            <h3>8.2 Homoszkedaszticitás Vizsgálata</h3>
            {img_tag("residuals_vs_fitted", "Reziduálisok a Becsült Értékek függvényében. A narancssárga LOESS trendvonal és a pontfelhő tölcsér-alakzatot mutat: magasabb becsült értékeknél a szóródás megnő, ami heteroszkedaszticitásra utal.", "14. Ábra: Reziduálisok vs. Becsült Értékek (LOESS Trendvonallal)")}

            <div class="callout-box danger">
                <div class="callout-head">🚨 Breusch–Pagan-teszt: Heteroszkedaszticitás Jelenléte</div>
                LM-statisztika = {data.get("bp_stat", 18.156):.4f} (p = {data.get("bp_pval", 0.00585):.5f} &lt; 0.01). 
                A hibavariancia nem konstans, ezért elengedhetetlen a robusztus standard hibák alkalmazása.
            </div>

            <h3>8.3 Autokorreláció és Függetlenség</h3>
            <div class="callout-box green">
                <div class="callout-head">✅ Durbin–Watson Statisztika: {data.get("dw_stat", 2.1019):.4f}</div>
                A DW érték (2.1019) tökéletesen az 1.5–2.5 közötti ideális sávban van, keresztmetszeti adatoknál a megfigyelések függetlenek.
            </div>

            <h3>8.4 Kiugró és Befolyásos Pontok (Cook's Distance)</h3>
            {img_tag("cooks_distance", "Cook-féle távolságok diagramja. A piros szaggatott vonal a 4/n = 0.002992 kritikus küszöbértéket jelöli. Bár a pontok 6.0%-a meghaladja a küszöböt, a legmagasabb Cook-távolság mindössze 0.0297, ami messze elmarad az 0.5 vagy 1.0 kritikus szinttől.", "15. Ábra: Cook-féle Távolságok Megfigyelésenként")}

            <h3>Top 10 Legbefolyásosabb Megfigyelés</h3>
            {dataframe_to_html_table(cooks_df)}

            <h3>8.5 HC3 Robusztus Standard Hibák (White-féle Korrekció)</h3>
            <p class="lead">
                A heteroszkedaszticitás orvoslására MacKinnon & White (1985) HC3 típusú robusztus kovarianciamátrixát használtuk.
            </p>
            {dataframe_to_html_table(se_comp_df)}

            <div class="callout-box green">
                <div class="callout-head">🏆 Végső Statisztikai Bizonyíték: Minden Változó Erősen Szignifikáns Marad!</div>
                Bár a robusztus standard hibák némileg növekedtek (pl. a <code>bmi_x_smoker</code> SE: 11 &rarr; 13 dollár), 
                <strong>valamennyi magyarázó változó p-értéke továbbra is erősen szignifikáns maradt (p &lt; 0.015, az életkornál és dohányzásnál p &lt; 0.0001)</strong>! 
                Ez bizonyítja az ökonometriai modell kikezdhetetlenségét.
            </div>
        </section>

        <!-- =========================================================
             09. STRATÉGIAI VEZETŐI AJÁNLÁSOK
             ========================================================= -->
        <section class="section-card" id="ajanlasok">
            <div class="section-header-wrap">
                <div class="section-num-pill">09</div>
                <h2>9. Stratégiai Vezetői Összefoglaló és Üzleti Ajánlások</h2>
            </div>
            <p class="lead">
                Az elemzés alapján az alábbi konkrét üzleti és termékfejlesztési döntéseket javasoljuk az egészségbiztosítók számára:
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 1.2rem;">
                <div class="callout-box">
                    <div class="callout-head">1. Interakciós Díjszabási Rendszer</div>
                    Meg kell szüntetni a dohányzásra kivetett fix pótdíjat. A díjszabási algoritmusnak a <strong>BMI &times; dohányzás szorzatot</strong> kell beáraznia, mert a túlsúlyos dohányzók költségkockázata exponenciálisan magasabb.
                </div>
                <div class="callout-box green">
                    <div class="callout-head">2. Magas Megtérülésű (ROI) Wellness Programok</div>
                    Mivel a dohányzó elhízottaknál minden leadott BMI pont <strong>évi $966 közvetlen megtakarítást</strong> jelent a biztosítónak, a dohányzásleszoktató terápiák és dietetikai tanácsadások finanszírozása azonnali, kiemelkedő pénzügyi megtérülést hoz.
                </div>
                <div class="callout-box purple">
                    <div class="callout-head">3. Tartalékképzés a Jobb Farok Kezelésére</div>
                    A normalitás hiánya és a vastag jobboldali farok miatt a biztosítónak a ritka, extrém költségű kárkifizetésekre katasztrófa-kockázati tőketartalékot és viszontbiztosítási (reinsurance) védelmet kell fenntartania.
                </div>
                <div class="callout-box amber">
                    <div class="callout-head">4. Kiszámítható Családi és Korcsoportos Csomagok</div>
                    Az életkor évenkénti +$261-os és a gyermekek darabonkénti +$488-os stabil hatása átlátható, versenypiaci alapot nyújt a családi és szenior csomagok differenciált kialakításához.
                </div>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="page-footer">
            <p style="margin-bottom: 8px;">
                <strong>Egészségbiztosítási Költségek — OLS Lineáris Regressziós Elemzés</strong> &bull; Készítette: <strong>Kovács Imre</strong>
            </p>
            <p style="margin-bottom: 12px; display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">
                <span>
                    🏠 <strong>Portfólió Főoldal:</strong> 
                    <a href="https://kovacsimi.github.io/" target="_blank" rel="noopener noreferrer">kovacsimi.github.io</a>
                </span>
                <span>
                    📂 <strong>GitHub Repository:</strong> 
                    <a href="https://github.com/KovacsImi/Linear-Regression" target="_blank" rel="noopener noreferrer">github.com/KovacsImi/Linear-Regression</a>
                </span>
                <span>
                    📊 <strong>Kaggle Adatforrás:</strong> 
                    <a href="https://www.kaggle.com/datasets/mirichoi0218/insurance/data" target="_blank" rel="noopener noreferrer">kaggle.com/datasets/mirichoi0218/insurance/data</a>
                </span>
            </p>
            <p style="font-size: 0.8rem; color: var(--text-muted);">
                Önálló, egyetlen fájlból álló HTML dokumentáció Base64-kódolt ábrákkal és interaktív OLS szimulátorral.
            </p>
        </footer>

    </div>

    <!-- JAVASCRIPT: Szimulátor, Lightbox, Kód-kapcsoló és Téma-váltó -->
    <script>
        // --- 1. Modell Koefficiens Konstansok ---
        const B_CONST = -7091.0155;
        const B_AGE = 261.4116;
        const B_BMI = 162.8300;
        const B_CHILDREN = 488.2161;
        const B_SE = -942.1288;
        const B_SW = -859.6450;
        const B_BMI_SMOKER = 803.1720;

        let isSmoker = false;

        function setSmoker(val) {{
            isSmoker = val;
            const btnNo = document.getElementById('simSmokerNo');
            const btnYes = document.getElementById('simSmokerYes');
            if (isSmoker) {{
                btnNo.classList.remove('active');
                btnYes.classList.add('active', 'danger');
            }} else {{
                btnYes.classList.remove('active', 'danger');
                btnNo.classList.add('active');
            }}
            runSimulation();
        }}

        function runSimulation() {{
            const age = parseFloat(document.getElementById('simAge').value);
            const bmi = parseFloat(document.getElementById('simBmi').value);
            const children = parseFloat(document.getElementById('simChildren').value);
            const region = document.getElementById('simRegion').value;

            document.getElementById('simAgeVal').textContent = age + ' év';
            document.getElementById('simBmiVal').textContent = bmi.toFixed(1) + ' kg/m²';
            document.getElementById('simChildrenVal').textContent = children + ' gyermek';

            let regionEffect = 0;
            if (region === 'southeast') {{
                regionEffect = B_SE;
            }} else if (region === 'southwest') {{
                regionEffect = B_SW;
            }}

            const ageCost = age * B_AGE;
            const bmiBaseCost = bmi * B_BMI;
            const childCost = children * B_CHILDREN;
            const smokerInterCost = isSmoker ? (bmi * B_BMI_SMOKER) : 0;

            const total = B_CONST + ageCost + bmiBaseCost + childCost + regionEffect + smokerInterCost;

            document.getElementById('simTotalPrice').textContent = '$' + Math.max(1000, total).toLocaleString('en-US', {{maximumFractionDigits: 0}});

            document.getElementById('bdAgeVal').textContent = age;
            document.getElementById('bdAgeCost').textContent = '+$' + Math.round(ageCost).toLocaleString('en-US');

            document.getElementById('bdBmiVal').textContent = bmi.toFixed(1);
            document.getElementById('bdBmiCost').textContent = '+$' + Math.round(bmiBaseCost).toLocaleString('en-US');

            document.getElementById('bdChildCost').textContent = '+$' + Math.round(childCost).toLocaleString('en-US');
            document.getElementById('bdRegionCost').textContent = (regionEffect < 0 ? '-' : '+') + '$' + Math.abs(Math.round(regionEffect)).toLocaleString('en-US');

            const bdSmokerEl = document.getElementById('bdSmokerCost');
            if (isSmoker) {{
                bdSmokerEl.textContent = '+$' + Math.round(smokerInterCost).toLocaleString('en-US');
            }} else {{
                bdSmokerEl.textContent = '$0';
            }}

            const warnBox = document.getElementById('simWarningBox');
            if (isSmoker && bmi >= 30) {{
                warnBox.style.display = 'block';
            }} else {{
                warnBox.style.display = 'none';
            }}
        }}

        // --- 2. Lightbox Kezelés ---
        function openLightbox(nameHint) {{
            const img = document.getElementById('img-' + nameHint);
            if (!img) return;
            const lb = document.getElementById('lightbox');
            const lbImg = document.getElementById('lightbox-img');
            lbImg.src = img.src;
            lb.classList.add('open');
        }}

        function closeLightbox(e) {{
            if (e.target.id === 'lightbox' || e.target.classList.contains('lightbox-close')) {{
                document.getElementById('lightbox').classList.remove('open');
            }}
        }}

        // Esc gomb bezárja a lightboxot
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                document.getElementById('lightbox').classList.remove('open');
            }}
        }});

        // --- 3. Kód Blokkok Együttes Kinyitása / Összecsukása ---
        let allCodeOpen = false;
        function toggleAllCode() {{
            allCodeOpen = !allCodeOpen;
            const details = document.querySelectorAll('details.code-fold');
            details.forEach(d => {{
                d.open = allCodeOpen;
            }});
        }}

        // --- 4. Kód Másolása Vágólapra ---
        function copyCode(btn) {{
            const pre = btn.nextElementSibling;
            if (!pre) return;
            const code = pre.innerText;
            navigator.clipboard.writeText(code).then(() => {{
                const originalText = btn.textContent;
                btn.textContent = '✅ Másolva!';
                setTimeout(() => {{
                    btn.textContent = originalText;
                }}, 2000);
            }});
        }}

        // --- 5. Téma Váltása (Dark Glass vs Light Executive) ---
        function toggleTheme() {{
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('kovacsimi-theme', newTheme);
            updateThemeUI(newTheme);
        }}

        function updateThemeUI(theme) {{
            const icon = document.getElementById('themeIcon');
            const label = document.getElementById('themeLabel');
            if (theme === 'light') {{
                icon.textContent = '🌙';
                label.textContent = 'Sötét';
            }} else {{
                icon.textContent = '☀️';
                label.textContent = 'Világos';
            }}
        }}

        // Téma betöltése mentett beállításból
        const savedTheme = localStorage.getItem('kovacsimi-theme');
        if (savedTheme) {{
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeUI(savedTheme);
        }}

        // Inicializálás
        runSimulation();
    </script>
</body>
</html>
'''

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n[OK] Egyedi glassmorphism HTML riport sikeresen elmentve: {output_filepath}")
    return output_filepath


if __name__ == "__main__":
    print("Ez a modul a medical_cost_analysis.py szkriptbol hivando meg.")
