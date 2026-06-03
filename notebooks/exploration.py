import pandas as pd

# Charger les données
df = pd.read_csv('videogames-analytics/data/raw/video_games_sales.csv')

# 1. Nombre de jeux
print(f"📊 Nombre de jeux : {len(df):,}")
print(f"   (ou avec shape : {df.shape[0]:,} lignes, {df.shape[1]} colonnes)")

# 2. Valeurs manquantes
print("\n❓ Valeurs manquantes :")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
missing_df = pd.DataFrame({'Manquantes': missing, '%': missing_pct})
print(missing_df[missing_df['Manquantes'] > 0])

# 3. Jeu le plus vendu
top_game = df.loc[df['Global_Sales'].idxmax()]
print(f"\n🏆 Jeu le plus vendu : {top_game['Name']}")
print(f"   Ventes : {top_game['Global_Sales']}M$ | Plateforme : {top_game['Platform']}")

# 4. Top 5 genres
print("\n🎯 Top 5 genres :")
print(df['Genre'].value_counts().head())

# 5. Plage d'années
min_year = df['Year_of_Release'].min()
max_year = df['Year_of_Release'].max()
print(f"\n📅 Années : {min_year:.0f} - {max_year:.0f}")