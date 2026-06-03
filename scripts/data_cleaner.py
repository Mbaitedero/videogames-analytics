import pandas as pd
import numpy as np
from pathlib import Path


class DataCleaner:
    def __init__(self, input_path=None, output_path=None):
        self.input_path = Path(input_path) if input_path else None
        self.output_path = Path(output_path) if output_path else None

    def clean_data(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Nettoie le dataset de jeux vidéo.
        Si df est fourni, l'utilise directement ; sinon lit depuis self.input_path.
        """
        print("🧹 Nettoyage des données...")

        if df is not None:
            df = df.copy()
        elif self.input_path:
            df = pd.read_csv(self.input_path)
        else:
            print("   Aucune source de données fournie.")
            return pd.DataFrame()

        initial_count = len(df)
        print(f"   Lignes initiales : {initial_count:,}")
        print(f"   Colonnes détectées : {df.columns.tolist()}")

        # 1. Supprimer les doublons
        dup_cols = [c for c in ['Name', 'Platform'] if c in df.columns]
        if dup_cols:
            df = df.drop_duplicates(subset=dup_cols)
            print(f"   Après déduplication : {len(df):,} (-{initial_count - len(df)})")

        # 2. Supprimer les lignes entièrement vides
        df = df.dropna(how='all')

        # 3. Normaliser le nom de la colonne année (Year ou Year_of_Release)
        if 'Year' in df.columns and 'Year_of_Release' not in df.columns:
            df = df.rename(columns={'Year': 'Year_of_Release'})
        if 'Year_of_Release' in df.columns:
            df['Year_of_Release'] = pd.to_numeric(df['Year_of_Release'], errors='coerce')
            df['Year_of_Release'] = df['Year_of_Release'].astype('Int64')

        # 4. Remplir les ventes manquantes par 0
        sales_cols = [c for c in ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales'] if c in df.columns]
        df[sales_cols] = df[sales_cols].fillna(0)

        # 5. Créer la décennie
        if 'Year_of_Release' in df.columns:
            df['Decade'] = (df['Year_of_Release'] // 10 * 10).astype('Int64')

        # 6. Créer la catégorie de ventes
        if 'Global_Sales' in df.columns:
            df['Sales_Category'] = pd.cut(
                df['Global_Sales'],
                bins=[-np.inf, 0.1, 1, 5, np.inf],
                labels=['Flop', 'Niche', 'Hit', 'Blockbuster']
            )

        # 7. Sauvegarder en Parquet
        if self.output_path is not None:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(self.output_path, index=False)
            print(f"   ✅ Sauvegardé : {self.output_path}")

        print(f"   Lignes finales : {len(df):,}")
        return df


if __name__ == "__main__":
    PROJECT_ROOT = Path('.')
    cleaned_df = DataCleaner(
        input_path=PROJECT_ROOT / 'data' / 'raw' / 'video_games_sales.csv',
        output_path=PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.parquet'
    ).clean_data()

    print("\n📊 Aperçu :")
    cols = [c for c in ['Name', 'Year_of_Release', 'Decade', 'Global_Sales', 'Sales_Category'] if c in cleaned_df.columns]
    print(cleaned_df[cols].head())