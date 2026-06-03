"""
🎮 Video Games Analytics Dashboard — Ultra Pro Edition
Dashboard Streamlit multi-pages avec design premium et visualisations avancées.
Remplace le dashboard existant dans : dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import subprocess
import sys
import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# INSTALLATION AUTO DES PACKAGES MANQUANTS
# ─────────────────────────────────────────────────────────────────────────────
def install_package(package):
    """Installe un package Python si manquant"""
    try:
        __import__(package)
    except ImportError:
        st.warning(f"Installation de {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        st.rerun()

# Vérifier et installer matplotlib si nécessaire
try:
    import matplotlib
    import matplotlib.colors as mcolors
except ImportError:
    install_package("matplotlib")
    import matplotlib
    import matplotlib.colors as mcolors

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VG Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THÈMES & PALETTE
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "🌑 Obsidian": {
        "bg":        "#0A0A0F",
        "surface":   "#13131E",
        "card":      "#1A1A2E",
        "border":    "#2A2A4A",
        "accent":    "#7C3AED",
        "accent2":   "#EC4899",
        "text":      "#E2E8F0",
        "subtext":   "#94A3B8",
        "chart_seq": "Purples",
        "chart_div": "RdPu",
        "bg_image":  "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070&auto=format&fit=crop",  # Cyberpunk gaming
    },
    "🔥 Ember": {
        "bg":        "#0D0805",
        "surface":   "#1A1008",
        "card":      "#241810",
        "border":    "#3D2A18",
        "accent":    "#F97316",
        "accent2":   "#EF4444",
        "text":      "#FEF3C7",
        "subtext":   "#D97706",
        "chart_seq": "Oranges",
        "chart_div": "YlOrRd",
        "bg_image":  "https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=2071&auto=format&fit=crop",  # Gaming fire
    },
    "🌊 Abyss": {
        "bg":        "#020B18",
        "surface":   "#071525",
        "card":      "#0C2040",
        "border":    "#163A6B",
        "accent":    "#38BDF8",
        "accent2":   "#34D399",
        "text":      "#E0F2FE",
        "subtext":   "#7DD3FC",
        "chart_seq": "Blues",
        "chart_div": "teal",
        "bg_image":  "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070&auto=format&fit=crop",  # Gaming deep
    },
    "💎 Arctic": {
        "bg":        "#F8FAFC",
        "surface":   "#F1F5F9",
        "card":      "#FFFFFF",
        "border":    "#CBD5E1",
        "accent":    "#6366F1",
        "accent2":   "#0EA5E9",
        "text":      "#0F172A",
        "subtext":   "#475569",
        "chart_seq": "Purples",
        "chart_div": "Bluered",
        "bg_image":  "https://images.unsplash.com/photo-1511882150382-421056c3c33b?q=80&w=2071&auto=format&fit=crop",  # Arctic gaming
    },
    "🌿 Matrix": {
        "bg":        "#020C02",
        "surface":   "#051505",
        "card":      "#091A09",
        "border":    "#14381A",
        "accent":    "#22C55E",
        "accent2":   "#84CC16",
        "text":      "#DCFCE7",
        "subtext":   "#86EFAC",
        "chart_seq": "Greens",
        "chart_div": "Greens",
        "bg_image":  "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?q=80&w=2070&auto=format&fit=crop",  # Matrix style
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — THÈME + NAVIGATION + FILTRES
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
      
    st.markdown("## 🎮 Video Game Analytics")
    st.markdown("---")

    theme_name = st.selectbox("🎨 Thème", list(THEMES.keys()), index=0)
    T = THEMES[theme_name]

    st.markdown("---")
    page = st.radio(
        "📑 Navigation",
        [
            "🏠 Vue d'ensemble",
            "📊 Genres & Plateformes",
            "🏢 Éditeurs",
            "🌍 Régions",
            "📈 Tendances temporelles",
            "🏆 Classements",
        ],
    )
    st.markdown("---")
    st.markdown("### 🔍 Filtres globaux")

# ─────────────────────────────────────────────────────────────────────────────
# CSS DYNAMIQUE AVEC IMAGE DE FOND
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');

/* Overlay sombre pour lisibilité sur l'image de fond */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('{T['bg_image']}') no-repeat center center fixed;
    background-size: cover;
    opacity: 0.15;
    z-index: -2;
}}

[data-testid="stAppViewContainer"]::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: {T['bg']};
    opacity: 0.85;
    z-index: -1;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: transparent !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(135deg, {T['surface']} 0%, {T['bg']} 100%) !important;
    border-right: 1px solid {T['border']};
    backdrop-filter: blur(10px);
}}

[data-testid="stSidebar"] * {{ color: {T['text']} !important; }}

/* Cartes avec effet glassmorphism */
[data-testid="stMetric"], [data-testid="stDataFrame"], div[data-testid="stVerticalBlock"] > div[style*="flex"] > div {{
    background: {T['card']};
    backdrop-filter: blur(10px);
    border: 1px solid {T['border']};
    border-radius: 16px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

[data-testid="stMetric"]:hover, [data-testid="stDataFrame"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}}

h1, h2, h3 {{
    font-family: 'Rajdhani', sans-serif !important;
    color: {T['accent']} !important;
    letter-spacing: 0.05em;
    text-shadow: 0 0 10px rgba(0,0,0,0.3);
}}

.section-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: {T['accent']};
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 2px solid {T['border']};
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}}

/* Animation d'entrée pour les KPIs */
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.kpi-card {{
    animation: fadeInUp 0.5s ease-out;
}}

/* Style personnalisé pour les badges */
.badge {{
    display: inline-block;
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    color: {T['bg']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 0.5rem;
}}

/* Scrollbar stylisée */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: {T['surface']};
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb {{
    background: {T['accent']};
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {T['accent2']};
}}

/* Style des sliders et selects */
.stSelectbox > div, .stSlider > div {{ color: {T['text']} !important; }}
[data-baseweb="select"] {{
    background: {T['card']} !important;
    border-color: {T['border']} !important;
    border-radius: 8px !important;
}}

/* Boutons stylisés */
.stButton > button {{
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: transform 0.2s ease;
}}
.stButton > button:hover {{
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DONNÉES
# ─────────────────────────────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000"

@st.cache_data(ttl=300)
def load_data():
    try:
        r = requests.get(f"{API_URL}/games?limit=10000", timeout=10)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            if "Year" in df.columns and "Year_of_Release" not in df.columns:
                df = df.rename(columns={"Year": "Year_of_Release"})
            return df
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_stats():
    try:
        r = requests.get(f"{API_URL}/stats/overview", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

def chart_layout(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=T["subtext"], size=12),
        title_font=dict(family="Rajdhani", color=T["text"], size=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["text"])),
        xaxis=dict(gridcolor=T["border"], color=T["subtext"]),
        yaxis=dict(gridcolor=T["border"], color=T["subtext"]),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig

with st.spinner("Chargement des données…"):
    df = load_data()
    stats = load_stats()

if df.empty:
    st.error("⚠️ Impossible de joindre l'API. Lance `uvicorn api.main:app --reload` puis actualise.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTRES GLOBAUX (sidebar suite)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    genres_all    = sorted(df["Genre"].dropna().unique()) if "Genre" in df.columns else []
    platforms_all = sorted(df["Platform"].dropna().unique()) if "Platform" in df.columns else []

    sel_genres = st.multiselect("Genre(s)", genres_all, default=genres_all)
    sel_plats  = st.multiselect("Plateforme(s)", platforms_all, default=platforms_all)

    if "Year_of_Release" in df.columns:
        years    = sorted(df["Year_of_Release"].dropna().astype(int).unique())
        yr_range = st.slider("Années", min(years), max(years), (min(years), max(years)))
    else:
        yr_range = None

    min_sales = st.slider("Ventes min (M$)", 0.0, float(df["Global_Sales"].max()), 0.0) \
        if "Global_Sales" in df.columns else 0.0

    st.markdown("---")
    st.markdown("### 📥 Export")
    if st.button("Préparer CSV"):
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Télécharger", csv, "vg_export.csv", "text/csv")

# Application des filtres
fd = df.copy()
if sel_genres:    fd = fd[fd["Genre"].isin(sel_genres)]
if sel_plats:     fd = fd[fd["Platform"].isin(sel_plats)]
if yr_range and "Year_of_Release" in fd.columns:
    fd = fd[fd["Year_of_Release"].fillna(0).astype(int).between(*yr_range)]
if "Global_Sales" in fd.columns:
    fd = fd[fd["Global_Sales"] >= min_sales]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — VUE D'ENSEMBLE
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Vue d'ensemble":
    st.markdown(f'<h1 style="font-family:Rajdhani;font-size:2.8rem;letter-spacing:.08em;">🎮 VIDEO GAMES ANALYTICS <span style="color:{T["accent2"]}">PRO</span></h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{T["subtext"]};font-family:JetBrains Mono;font-size:.8rem;">{len(fd):,} jeux · données filtrées · thème {theme_name}</p>', unsafe_allow_html=True)

    # KPIs avec animation
    top_game  = fd.loc[fd["Global_Sales"].idxmax(), "Name"] if not fd.empty else "N/A"
    top_pub   = fd.groupby("Publisher")["Global_Sales"].sum().idxmax() if "Publisher" in fd.columns else "N/A"
    top_genre = fd.groupby("Genre")["Global_Sales"].sum().idxmax() if "Genre" in fd.columns else "N/A"
    total_s   = fd["Global_Sales"].sum() if "Global_Sales" in fd.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("🎮 Jeux", f"{len(fd):,}")
    with c2: st.metric("💰 Ventes Totales", f"{total_s:,.0f}M$")
    with c3: st.metric("🏢 Éditeurs", f"{fd['Publisher'].nunique():,}" if "Publisher" in fd.columns else "N/A")
    with c4: st.metric("🕹️ Plateformes", f"{fd['Platform'].nunique():,}" if "Platform" in fd.columns else "N/A")
    with c5: st.metric("🏆 Top Jeu", top_game[:20] + "…" if len(top_game) > 20 else top_game)

    st.markdown('<div class="section-title">Aperçu Général</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        # Treemap genres
        if "Genre" in fd.columns and "Global_Sales" in fd.columns:
            gd = fd.groupby("Genre", as_index=False)["Global_Sales"].sum()
            fig = px.treemap(gd, path=["Genre"], values="Global_Sales",
                             color="Global_Sales", color_continuous_scale=T["chart_seq"],
                             title="🌳 Poids des Genres (Ventes $M)")
            chart_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Sales category donut
        if "Sales_Category" in fd.columns:
            sc = fd["Sales_Category"].value_counts()
            fig = go.Figure(go.Pie(
                labels=sc.index, values=sc.values, hole=0.55,
                marker_colors=[T["accent"], T["accent2"], "#64748B", "#0EA5E9"],
                textfont=dict(family="Rajdhani", size=14),
            ))
            fig.update_layout(title="🏷️ Catégories de Ventes",
                              annotations=[dict(text="Catégories", x=0.5, y=0.5,
                                               font=dict(size=14, color=T["text"], family="Rajdhani"),
                                               showarrow=False)])
            chart_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    # Scatter global
    st.markdown('<div class="section-title">Dispersion par Genre & Plateforme</div>', unsafe_allow_html=True)
    if {"Genre", "Global_Sales", "Platform"}.issubset(fd.columns):
        sample = fd.nlargest(500, "Global_Sales")
        fig = px.scatter(
            sample, x="Year_of_Release", y="Global_Sales",
            color="Genre", size="Global_Sales", hover_name="Name",
            size_max=40, opacity=0.8,
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Scatter : Ventes par Année & Genre (Top 500)",
        )
        chart_layout(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — GENRES & PLATEFORMES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Genres & Plateformes":
    st.markdown("# 📊 Genres & Plateformes")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Ventes Totales par Genre</div>', unsafe_allow_html=True)
        gs = fd.groupby("Genre")["Global_Sales"].sum().sort_values()
        fig = px.bar(gs, x=gs.values, y=gs.index, orientation="h",
                     color=gs.values, color_continuous_scale=T["chart_seq"],
                     labels={"x": "Ventes ($M)", "y": ""})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Nombre de Jeux par Genre</div>', unsafe_allow_html=True)
        gc = fd["Genre"].value_counts()
        fig = px.bar(gc, x=gc.index, y=gc.values, color=gc.values,
                     color_continuous_scale=T["chart_seq"],
                     labels={"x": "Genre", "y": "Nb Jeux"})
        fig.update_layout(xaxis_tickangle=-35)
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Ventes Moyennes par Genre</div>', unsafe_allow_html=True)
    avg_g = fd.groupby("Genre")["Global_Sales"].mean().sort_values(ascending=False)
    fig = go.Figure(go.Bar(
        x=avg_g.index, y=avg_g.values,
        marker=dict(
            color=avg_g.values,
            colorscale=T["chart_seq"],
            showscale=True,
            line=dict(color=T["accent"], width=1),
        ),
    ))
    fig.update_layout(title="Ventes moyennes par genre (M$)")
    chart_layout(fig, 350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Top 15 Plateformes par Ventes</div>', unsafe_allow_html=True)
    if "Platform" in fd.columns:
        ps = fd.groupby("Platform")["Global_Sales"].sum().nlargest(15)
        fig = px.bar(ps, x=ps.index, y=ps.values,
                     color=ps.values, color_continuous_scale=T["chart_div"],
                     labels={"x": "Plateforme", "y": "Ventes ($M)"})
        chart_layout(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap genre × plateforme
    st.markdown('<div class="section-title">Heatmap Genre × Plateforme</div>', unsafe_allow_html=True)
    if {"Genre", "Platform", "Global_Sales"}.issubset(fd.columns):
        top_plats = fd.groupby("Platform")["Global_Sales"].sum().nlargest(15).index
        heat_df = fd[fd["Platform"].isin(top_plats)]
        pivot = heat_df.pivot_table(index="Genre", columns="Platform",
                                    values="Global_Sales", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, color_continuous_scale=T["chart_seq"],
                        aspect="auto", title="Ventes ($M) par Genre & Plateforme")
        chart_layout(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — ÉDITEURS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏢 Éditeurs":
    st.markdown("# 🏢 Analyse des Éditeurs")

    if "Publisher" not in fd.columns:
        st.error("Colonne Publisher absente.")
        st.stop()

    pub_df = (
        fd.groupby("Publisher")
        .agg(
            jeux=("Name", "count"),
            ventes=("Global_Sales", "sum"),
            ventes_moy=("Global_Sales", "mean"),
            genres=("Genre", "nunique"),
            plateformes=("Platform", "nunique"),
        )
        .reset_index()
        .sort_values("ventes", ascending=False)
    )

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🏢 Éditeurs", f"{len(pub_df):,}")
    with c2: st.metric("🥇 Leader", pub_df.iloc[0]["Publisher"])
    with c3: st.metric("💰 Ventes Leader", f"{pub_df.iloc[0]['ventes']:,.0f}M$")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Top 15 Éditeurs — Ventes Totales</div>', unsafe_allow_html=True)
        top15 = pub_df.head(15)
        fig = px.bar(top15, x="ventes", y="Publisher", orientation="h",
                     color="ventes", color_continuous_scale=T["chart_seq"],
                     text="jeux", labels={"ventes": "Ventes ($M)", "jeux": "Nb jeux"})
        fig.update_traces(texttemplate="%{text} jeux", textposition="inside")
        chart_layout(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Parts de Marché — Top 10</div>', unsafe_allow_html=True)
        top10 = pub_df.head(10)
        others = pub_df.iloc[10:]["ventes"].sum()
        labels = list(top10["Publisher"]) + ["Autres"]
        vals   = list(top10["ventes"]) + [others]
        fig = go.Figure(go.Pie(
            labels=labels, values=vals, hole=0.45,
            pull=[0.05] + [0] * 10,
            marker_colors=px.colors.qualitative.Bold,
        ))
        chart_layout(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Efficacité : Ventes Moy. vs Volume (Top 30)</div>', unsafe_allow_html=True)
    top30 = pub_df[pub_df["jeux"] >= 10].head(30)
    fig = px.scatter(
        top30, x="jeux", y="ventes_moy", size="ventes",
        text="Publisher", color="genres",
        color_continuous_scale=T["chart_seq"],
        labels={"jeux": "Nb de Jeux", "ventes_moy": "Ventes Moy ($M)", "genres": "Genres"},
        title="Bubble chart — Éditeurs : Volume vs Efficacité",
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    chart_layout(fig, 550)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Tableau Détaillé Éditeurs</div>', unsafe_allow_html=True)
    # Correction: remplacer background_gradient par une alternative sans matplotlib
    df_display = pub_df.head(50).rename(columns={
        "Publisher": "Éditeur", "jeux": "Jeux",
        "ventes": "Ventes ($M)", "ventes_moy": "Ventes Moy ($M)",
        "genres": "Genres", "plateformes": "Plateformes",
    }).copy()
    
    # Formatage sans gradient
    formatted_df = df_display.style.format({
        "Ventes ($M)": "{:.1f}", 
        "Ventes Moy ($M)": "{:.2f}"
    })
    st.dataframe(formatted_df, use_container_width=True, height=400)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — RÉGIONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🌍 Régions":
    st.markdown("# 🌍 Analyse Régionale")

    region_map = {
        "NA_Sales":    "Amérique du Nord",
        "EU_Sales":    "Europe",
        "JP_Sales":    "Japon",
        "Other_Sales": "Autres",
    }
    regions = [c for c in region_map if c in fd.columns]

    if not regions:
        st.error("Aucune colonne régionale trouvée.")
        st.stop()

    totals = fd[regions].sum()
    labels = [region_map[r] for r in regions]

    c1, c2, c3, c4 = st.columns(4)
    for col, reg, lbl in zip([c1, c2, c3, c4], regions, labels):
        with col:
            pct = totals[reg] / totals.sum() * 100
            st.metric(lbl, f"{totals[reg]:,.0f}M$", f"{pct:.1f}% du total")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Répartition Régionale Globale</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=labels, values=totals.values, hole=0.5,
            marker_colors=[T["accent"], T["accent2"], "#34D399", "#F59E0B"],
        ))
        fig.update_layout(annotations=[dict(text="Régions", x=0.5, y=0.5, showarrow=False,
                                            font=dict(size=14, color=T["text"], family="Rajdhani"))])
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Ventes par Genre & Région</div>', unsafe_allow_html=True)
        if "Genre" in fd.columns:
            gr = fd.groupby("Genre")[regions].sum().reset_index()
            fig = go.Figure()
            colors = [T["accent"], T["accent2"], "#34D399", "#F59E0B"]
            for reg, lbl, col in zip(regions, labels, colors):
                fig.add_trace(go.Bar(name=lbl, x=gr["Genre"], y=gr[reg], marker_color=col))
            fig.update_layout(barmode="stack", title="Ventes empilées par Genre & Région")
            chart_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    # Comparatif NA vs JP
    st.markdown('<div class="section-title">Comparatif NA vs Japon — Top 20 Jeux</div>', unsafe_allow_html=True)
    if {"NA_Sales", "JP_Sales", "Name"}.issubset(fd.columns):
        top20 = fd.nlargest(20, "Global_Sales")[["Name", "NA_Sales", "JP_Sales"]].set_index("Name")
        fig = go.Figure()
        fig.add_trace(go.Bar(name="NA", y=top20.index, x=top20["NA_Sales"],
                             orientation="h", marker_color=T["accent"]))
        fig.add_trace(go.Bar(name="Japon", y=top20.index, x=-top20["JP_Sales"],
                             orientation="h", marker_color=T["accent2"]))
        fig.update_layout(barmode="overlay", title="Comparatif NA (↑) vs Japon (↓)",
                          xaxis=dict(tickvals=[-15, -10, -5, 0, 5, 10, 15, 20, 25],
                                     ticktext=["15", "10", "5", "0", "5", "10", "15", "20", "25"]))
        chart_layout(fig, 550)
        st.plotly_chart(fig, use_container_width=True)

    # Radar par région & genre
    st.markdown('<div class="section-title">Radar : Profil Régional par Genre</div>', unsafe_allow_html=True)
    if "Genre" in fd.columns:
        top_genres = fd.groupby("Genre")["Global_Sales"].sum().nlargest(8).index.tolist()
        fd_radar = fd[fd["Genre"].isin(top_genres)]
        fig = go.Figure()
        colors = [T["accent"], T["accent2"], "#34D399", "#F59E0B"]
        for reg, lbl, col in zip(regions, labels, colors):
            vals = [fd_radar[fd_radar["Genre"] == g][reg].sum() for g in top_genres]
            # Convertir la couleur hex en rgba pour l'opacité
            r = int(col[1:3], 16) if col.startswith('#') else 99
            g = int(col[3:5], 16) if col.startswith('#') else 102
            b = int(col[5:7], 16) if col.startswith('#') else 241
            fillcolor_rgba = f"rgba({r}, {g}, {b}, 0.15)"
            fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=top_genres + [top_genres[0]],
                                          fill="toself", name=lbl,
                                          line_color=col, fillcolor=fillcolor_rgba))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                     radialaxis=dict(gridcolor=T["border"], color=T["subtext"]),
                                     angularaxis=dict(gridcolor=T["border"])))
        chart_layout(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — TENDANCES TEMPORELLES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Tendances temporelles":
    st.markdown("# 📈 Tendances Temporelles")

    if "Year_of_Release" not in fd.columns:
        st.error("Colonne Year_of_Release absente.")
        st.stop()

    tfd = fd.dropna(subset=["Year_of_Release"]).copy()
    tfd["Year"] = tfd["Year_of_Release"].astype(int)

    yearly = tfd.groupby("Year").agg(
        ventes=("Global_Sales", "sum"),
        jeux=("Name", "count"),
        vente_moy=("Global_Sales", "mean"),
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Ventes Totales par Année</div>', unsafe_allow_html=True)
        fig = px.area(yearly, x="Year", y="ventes",
                      color_discrete_sequence=[T["accent"]],
                      title="Évolution des ventes annuelles ($M)")
        # Conversion hex vers rgba
        r = int(T['accent'][1:3], 16) if T['accent'].startswith('#') else 99
        g = int(T['accent'][3:5], 16) if T['accent'].startswith('#') else 102
        b = int(T['accent'][5:7], 16) if T['accent'].startswith('#') else 241
        fig.update_traces(fill="tozeroy", fillcolor=f"rgba({r}, {g}, {b}, 0.13)", line_width=2)
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Nombre de Sorties par Année</div>', unsafe_allow_html=True)
        fig = px.bar(yearly, x="Year", y="jeux",
                     color="jeux", color_continuous_scale=T["chart_seq"],
                     title="Nombre de jeux sortis par année")
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Évolution par Genre dans le Temps</div>', unsafe_allow_html=True)
    if "Genre" in tfd.columns:
        gy = tfd.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
        top_g = tfd.groupby("Genre")["Global_Sales"].sum().nlargest(6).index
        gy = gy[gy["Genre"].isin(top_g)]
        fig = px.line(gy, x="Year", y="Global_Sales", color="Genre",
                      color_discrete_sequence=px.colors.qualitative.Bold,
                      markers=True, title="Ventes par genre au fil des années")
        chart_layout(fig, 450)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Ventes Moyennes par Année</div>', unsafe_allow_html=True)
        fig = px.line(yearly, x="Year", y="vente_moy",
                      color_discrete_sequence=[T["accent2"]],
                      title="Vente moyenne par jeu ($M)", markers=True)
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Plateformes Dominantes par Décennie</div>', unsafe_allow_html=True)
        if "Platform" in tfd.columns and "Decade" in tfd.columns:
            dec = tfd.groupby(["Decade", "Platform"])["Global_Sales"].sum().reset_index()
            top_per_dec = dec.sort_values("Global_Sales", ascending=False).groupby("Decade").head(5)
            fig = px.bar(top_per_dec, x="Decade", y="Global_Sales", color="Platform",
                         color_discrete_sequence=px.colors.qualitative.Bold,
                         title="Top plateformes par décennie")
            chart_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE — CLASSEMENTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏆 Classements":
    st.markdown("# 🏆 Classements")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Top 20 Jeux Tous Temps</div>', unsafe_allow_html=True)
        top20 = fd.nlargest(20, "Global_Sales")[["Name", "Platform", "Genre", "Publisher", "Global_Sales"]]
        fig = px.bar(top20, x="Global_Sales", y="Name", orientation="h",
                     color="Genre", color_discrete_sequence=px.colors.qualitative.Bold,
                     text="Global_Sales", labels={"Global_Sales": "Ventes ($M)", "Name": ""})
        fig.update_traces(texttemplate="%{x:.1f}M$", textposition="outside")
        chart_layout(fig, 600)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Top Jeu par Genre</div>', unsafe_allow_html=True)
        if "Genre" in fd.columns:
            top_genre = (
                fd.sort_values("Global_Sales", ascending=False)
                .groupby("Genre")
                .first()
                .reset_index()[["Genre", "Name", "Global_Sales", "Platform"]]
                .sort_values("Global_Sales", ascending=False)
            )
            fig = px.bar(top_genre, x="Global_Sales", y="Genre", orientation="h",
                         color="Global_Sales", color_continuous_scale=T["chart_seq"],
                         text="Name", labels={"Global_Sales": "Ventes ($M)"})
            fig.update_traces(textposition="inside", textfont_size=10)
            chart_layout(fig, 600)
            st.plotly_chart(fig, use_container_width=True)

    # Top 50 tableau interactif avec gradient
    st.markdown('<div class="section-title">Top 50 — Tableau Interactif</div>', unsafe_allow_html=True)
    disp = [c for c in ["Name", "Platform", "Genre", "Publisher", "Year_of_Release", "Global_Sales",
                        "NA_Sales", "EU_Sales", "JP_Sales", "Sales_Category"] if c in fd.columns]
    top50 = fd.nlargest(50, "Global_Sales")[disp].reset_index(drop=True)
    top50.index = top50.index + 1

    # Application du gradient (maintenant que matplotlib est installé)
    st.dataframe(
        top50.style.background_gradient(
            subset=["Global_Sales"], 
            cmap="Purples"
        ).format({
            "Global_Sales": "{:.2f}", 
            "NA_Sales": "{:.2f}",
            "EU_Sales": "{:.2f}", 
            "JP_Sales": "{:.2f}"
            }),
        use_container_width=True, 
        height=500,
    )

    st.markdown('<div class="section-title">Flop 20 — Jeux les Moins Vendus</div>', unsafe_allow_html=True)
    flop = fd[fd["Global_Sales"] > 0].nsmallest(20, "Global_Sales")[
        ["Name", "Platform", "Genre", "Global_Sales"]].reset_index(drop=True)
    fig = px.bar(flop, x="Global_Sales", y="Name", orientation="h",
                 color="Genre", color_discrete_sequence=px.colors.qualitative.Pastel,
                 title="20 jeux avec les ventes les plus basses")
    chart_layout(fig, 500)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p style="text-align:center;color:{T["subtext"]};font-family:JetBrains Mono;font-size:.75rem;">'
    f"Video Games Analytics Pro — Data Engineering Bootcamp — {len(fd):,} jeux analysés</p>",
    unsafe_allow_html=True,
)