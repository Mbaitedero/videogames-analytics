"""
Module de chargement des données avec validation et logging améliorés
Améliorations:
- Validation des données à l'import
- Gestion des erreurs robuste
- Logging structuré
- Support de multiples formats
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any
import yaml

class DataLoader:
    """Chargeur de données avec validation et monitoring"""
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.add(self.config['paths']['logs'], rotation="10 MB")
        logger.info("DataLoader initialisé")
    
    def load_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Charge un fichier CSV avec validation
        
        Améliorations:
        - Vérification de l'existence du fichier
        - Détection automatique de l'encodage
        - Gestion des erreurs granulaire
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
            
            logger.info(f"Chargement de {file_path}")
            
            # Détection automatique de l'encodage
            import chardet
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read(10000))
                encoding = result['encoding']
            
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Validation basique
            if df.empty:
                raise ValueError("Le fichier CSV est vide")
            
            logger.success(f"Chargé {len(df)} lignes, {len(df.columns)} colonnes")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            return None
    
    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valide le schéma des données"""
        expected_columns = [
            'Name', 'Platform', 'Year_of_Release', 'Genre', 'Publisher',
            'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales',
            'Critic_Score', 'User_Score', 'Rating'
        ]
        
        report = {
            'missing_columns': [],
            'extra_columns': [],
            'dtype_issues': [],
            'total_missing': df.isnull().sum().to_dict()
        }
        
        # Vérification des colonnes
        for col in expected_columns:
            if col not in df.columns:
                report['missing_columns'].append(col)
        
        for col in df.columns:
            if col not in expected_columns:
                report['extra_columns'].append(col)
        
        logger.info(f"Validation terminée: {len(report['missing_columns'])} colonnes manquantes")
        return report

# Fonction utilitaire pour générer des données de test
def generate_sample_data(n_rows: int = 1000) -> pd.DataFrame:
    """Génère des données d'exemple pour les tests"""
    np.random.seed(42)
    
    games = [
        "Super Mario", "Pokemon", "Grand Theft Auto", "Call of Duty",
        "FIFA", "Minecraft", "The Legend of Zelda", "Red Dead Redemption"
    ]
    platforms = ['PS4', 'Xbox One', 'PC', 'Switch', 'PS5']
    genres = ['Action', 'Sports', 'RPG', 'Shooter', 'Adventure']
    publishers = ['Nintendo', 'Sony', 'Microsoft', 'EA', 'Ubisoft']
    ratings = ['E', 'T', 'M', 'E10+']
    
    data = {
        'Name': np.random.choice(games, n_rows),
        'Platform': np.random.choice(platforms, n_rows),
        'Year_of_Release': np.random.randint(2000, 2024, n_rows),
        'Genre': np.random.choice(genres, n_rows),
        'Publisher': np.random.choice(publishers, n_rows),
        'NA_Sales': np.random.uniform(0, 10, n_rows),
        'EU_Sales': np.random.uniform(0, 8, n_rows),
        'JP_Sales': np.random.uniform(0, 5, n_rows),
        'Other_Sales': np.random.uniform(0, 3, n_rows),
        'Critic_Score': np.random.uniform(0, 100, n_rows),
        'User_Score': np.random.uniform(0, 10, n_rows),
        'Rating': np.random.choice(ratings, n_rows)
    }
    
    df = pd.DataFrame(data)
    df['Global_Sales'] = df[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum(axis=1)
    
    return df