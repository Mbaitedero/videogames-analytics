"""Composants réutilisables pour le dashboard Streamlit"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple, Optional

def render_sidebar_filters(df: pd.DataFrame) -> Dict:
    """
    Renders the sidebar with filters and returns selected filter values
    
    Returns:
        Dict with filter values: genre, platform, year_range, min_sales
    """
    st.sidebar.markdown("## 🎮 Filtres")
    st.sidebar.markdown("---")
    
    # Filtre Genre
    genres = ['Tous'] + sorted(df['Genre'].dropna().unique().tolist())
    selected_genre = st.sidebar.selectbox(
        "🎭 Genre", 
        genres,
        help="Filtrer par genre de jeu"
    )
    
    # Filtre Plateforme
    platforms = ['Toutes'] + sorted(df['Platform'].dropna().unique().tolist())
    selected_platform = st.sidebar.selectbox(
        "🕹️ Plateforme", 
        platforms,
        help="Filtrer par plateforme de jeu"
    )
    
    st.sidebar.markdown("---")
    
    # Filtre Années
    year_min = int(df['Year_of_Release'].min())
    year_max = int(df['Year_of_Release'].max())
    selected_years = st.sidebar.slider(
        "📅 Période",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        help="Sélectionner une plage d'années"
    )
    
    st.sidebar.markdown("---")
    
    # Filtre Ventes
    max_sales = float(df['Global_Sales'].max())
    min_sales = st.sidebar.slider(
        "💰 Ventes minimum (millions)",
        min_value=0.0,
        max_value=max_sales,
        value=0.0,
        step=0.5,
        help="Filtrer par ventes mondiales"
    )
    
    # Filtre Score
    if 'Critic_Score' in df.columns:
        st.sidebar.markdown("---")
        min_score = st.sidebar.slider(
            "⭐ Score minimum",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=5.0,
            help="Filtrer par score Metacritic"
        )
    else:
        min_score = 0
    
    # Filtre Éditeur (optionnel - top 20 par ventes)
    st.sidebar.markdown("---")
    top_publishers = df.groupby('Publisher')['Global_Sales'].sum().nlargest(20).index.tolist()
    publishers = ['Tous'] + sorted(top_publishers)
    selected_publisher = st.sidebar.selectbox(
        "🏢 Éditeur",
        publishers,
        help="Filtrer par éditeur (top 20)"
    )
    
    return {
        'genre': selected_genre,
        'platform': selected_platform,
        'year_range': selected_years,
        'min_sales': min_sales,
        'min_score': min_score,
        'publisher': selected_publisher
    }

def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply filters to the dataframe"""
    filtered_df = df.copy()
    
    if filters['genre'] != 'Tous':
        filtered_df = filtered_df[filtered_df['Genre'] == filters['genre']]
    
    if filters['platform'] != 'Toutes':
        filtered_df = filtered_df[filtered_df['Platform'] == filters['platform']]
    
    if filters['publisher'] != 'Tous':
        filtered_df = filtered_df[filtered_df['Publisher'] == filters['publisher']]
    
    filtered_df = filtered_df[
        (filtered_df['Year_of_Release'] >= filters['year_range'][0]) &
        (filtered_df['Year_of_Release'] <= filters['year_range'][1]) &
        (filtered_df['Global_Sales'] >= filters['min_sales'])
    ]
    
    if filters['min_score'] > 0 and 'Critic_Score' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Critic_Score'] >= filters['min_score']]
    
    return filtered_df

def render_kpi_cards(df: pd.DataFrame):
    """Display KPI cards at the top of the dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; padding: 1rem; text-align: center;">
                <h3 style="margin:0; color:white;">🎮</h3>
                <h2 style="margin:0; color:white;">{}</h2>
                <p style="margin:0; color:rgba(255,255,255,0.8);">Jeux</p>
            </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        border-radius: 15px; padding: 1rem; text-align: center;">
                <h3 style="margin:0; color:white;">💰</h3>
                <h2 style="margin:0; color:white;">{:.1f}M</h2>
                <p style="margin:0; color:rgba(255,255,255,0.8);">Ventes totales</p>
            </div>
        """.format(df['Global_Sales'].sum()), unsafe_allow_html=True)
    
    with col3:
        avg_score = df['Critic_Score'].mean() if 'Critic_Score' in df.columns and df['Critic_Score'].notna().any() else 0
        st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        border-radius: 15px; padding: 1rem; text-align: center;">
                <h3 style="margin:0; color:white;">⭐</h3>
                <h2 style="margin:0; color:white;">{:.1f}</h2>
                <p style="margin:0; color:rgba(255,255,255,0.8);">Score moyen</p>
            </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    with col4:
        top_game = df.loc[df['Global_Sales'].idxmax(), 'Name'] if not df.empty else "N/A"
        top_sales = df['Global_Sales'].max() if not df.empty else 0
        st.markdown("""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        border-radius: 15px; padding: 1rem; text-align: center;">
                <h3 style="margin:0; color:white;">🏆</h3>
                <h2 style="margin:0; color:white; font-size:1.2rem;">{}</h2>
                <p style="margin:0; color:rgba(255,255,255,0.8);">{:.1f}M ventes</p>
            </div>
        """.format(top_game[:15] + "..." if len(top_game) > 15 else top_game, top_sales), unsafe_allow_html=True)

def render_sales_by_genre_chart(df: pd.DataFrame):
    """Render bar chart of sales by genre"""
    genre_sales = df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=True)
    
    fig = px.bar(
        genre_sales,
        x='Global_Sales',
        y=genre_sales.index,
        orientation='h',
        color=genre_sales.values,
        color_continuous_scale='Viridis',
        title="💰 Ventes totales par genre",
        labels={'Global_Sales': 'Ventes (millions)', 'Genre': ''}
    )
    fig.update_layout(height=450, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

def render_sales_trend_chart(df: pd.DataFrame):
    """Render line chart of sales over time"""
    yearly_sales = df.groupby('Year_of_Release')['Global_Sales'].sum().reset_index()
    
    fig = px.line(
        yearly_sales,
        x='Year_of_Release',
        y='Global_Sales',
        title="📈 Évolution des ventes dans le temps",
        markers=True,
        labels={'Year_of_Release': 'Année', 'Global_Sales': 'Ventes (millions)'}
    )
    fig.update_traces(line=dict(width=3, color='#FF4B4B'), marker=dict(size=8))
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

def render_top_games_table(df: pd.DataFrame, limit: int = 10):
    """Render table of top games"""
    top_games = df.nlargest(limit, 'Global_Sales')[
        ['Name', 'Platform', 'Genre', 'Publisher', 'Year_of_Release', 'Global_Sales', 'Critic_Score', 'Sales_Category']
    ].copy()
    
    # Formatage
    top_games['Global_Sales'] = top_games['Global_Sales'].apply(lambda x: f"{x:.1f}M")
    top_games['Critic_Score'] = top_games['Critic_Score'].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "N/A")
    
    st.dataframe(
        top_games,
        use_container_width=True,
        column_config={
            "Name": "🎮 Jeu",
            "Platform": "🕹️ Plateforme",
            "Genre": "🎭 Genre",
            "Publisher": "🏢 Éditeur",
            "Year_of_Release": "📅 Année",
            "Global_Sales": "💰 Ventes",
            "Critic_Score": "⭐ Score",
            "Sales_Category": "🏷️ Catégorie"
        }
    )

def render_region_pie_chart(df: pd.DataFrame):
    """Render pie chart of sales by region"""
    region_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']
    region_names = ['Amérique du Nord', 'Europe', 'Japon', 'Autres']
    region_totals = [df[col].sum() for col in region_cols]
    
    fig = px.pie(
        values=region_totals,
        names=region_names,
        title="🌍 Distribution des ventes par région",
        color_discrete_sequence=px.colors.sequential.Viridis,
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

def render_score_distribution(df: pd.DataFrame):
    """Render histogram of critic scores"""
    scores = df[df['Critic_Score'].notna()]['Critic_Score']
    
    fig = px.histogram(
        scores,
        nbins=30,
        title="⭐ Distribution des scores Metacritic",
        labels={'value': 'Score', 'count': 'Nombre de jeux'},
        color_discrete_sequence=['#FF4B4B']
    )
    fig.update_layout(height=400, bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)

def render_publisher_chart(df: pd.DataFrame):
    """Render bar chart of top publishers"""
    top_publishers = df.groupby('Publisher')['Global_Sales'].sum().nlargest(10)
    
    fig = px.bar(
        top_publishers,
        x=top_publishers.values,
        y=top_publishers.index,
        orientation='h',
        title="🏢 Top 10 des éditeurs par ventes",
        labels={'x': 'Ventes (millions)', 'y': ''},
        color=top_publishers.values,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=450, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

def render_download_button(df: pd.DataFrame, filename: str = "videogames_export.csv"):
    """Render download button for filtered data"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger les données (CSV)",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )

def render_footer():
    """Render the dashboard footer"""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: gray; padding: 1rem;">
            <p>🎮 Video Games Analytics Platform | Data Engineering Bootcamp</p>
            <p style="font-size: 0.8rem;">Données de ventes de jeux vidéo 1980-2024</p>
        </div>
        """,
        unsafe_allow_html=True
    )