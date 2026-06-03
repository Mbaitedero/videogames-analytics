"""Module de connexion à la base de données DuckDB"""

import duckdb
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class DatabaseManager:
    """Gestionnaire de connexion à DuckDB"""
    
    def __init__(self, db_path: str = "data/videogames.db"):
        self.db_path = Path(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Vérifie que la base de données existe"""
        if not self.db_path.exists():
            logger.warning(f"Base de données non trouvée: {self.db_path}")
            self._create_from_parquet()
    
    def _create_from_parquet(self):
        """Crée la base à partir du fichier Parquet nettoyé"""
        parquet_path = Path("data/processed/clean_games.parquet")
        
        if parquet_path.exists():
            logger.info(f"Création de la base depuis {parquet_path}")
            conn = duckdb.connect(str(self.db_path))
            
            try:
                df = pd.read_parquet(parquet_path)
                conn.register('temp_df', df)
                conn.execute("CREATE OR REPLACE TABLE games AS SELECT * FROM temp_df")
                
                # Créer des index pour les performances
                conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON games(Name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_genre ON games(Genre)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_platform ON games(Platform)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON games(Year_of_Release)")
                
                count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
                logger.success(f"Base créée: {count} jeux")
            except Exception as e:
                logger.error(f"Erreur création base: {e}")
            finally:
                conn.close()
        else:
            logger.error(f"Fichier Parquet non trouvé: {parquet_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions"""
        conn = None
        try:
            conn = duckdb.connect(str(self.db_path))
            yield conn
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: List = None) -> pd.DataFrame:
        """Exécute une requête et retourne un DataFrame"""
        with self.get_connection() as conn:
            if params:
                return conn.execute(query, params).fetchdf()
            else:
                return conn.execute(query).fetchdf()
    
    def get_game_by_name(self, name: str) -> Optional[Dict]:
        """Récupère un jeu par son nom"""
        query = "SELECT * FROM games WHERE Name = ? LIMIT 1"
        df = self.execute_query(query, [name])
        return df.iloc[0].to_dict() if not df.empty else None
    
    def get_games_with_filters(self, filters: Dict, limit: int = 50, offset: int = 0) -> pd.DataFrame:
        """Récupère les jeux avec filtres"""
        query = "SELECT * FROM games WHERE 1=1"
        params = []
        
        if filters.get('genre'):
            query += " AND Genre = ?"
            params.append(filters['genre'])
        
        if filters.get('platform'):
            query += " AND Platform = ?"
            params.append(filters['platform'])
        
        if filters.get('publisher'):
            query += " AND Publisher = ?"
            params.append(filters['publisher'])
        
        if filters.get('min_sales'):
            query += " AND Global_Sales >= ?"
            params.append(filters['min_sales'])
        
        if filters.get('max_sales'):
            query += " AND Global_Sales <= ?"
            params.append(filters['max_sales'])
        
        if filters.get('min_year'):
            query += " AND Year_of_Release >= ?"
            params.append(filters['min_year'])
        
        if filters.get('max_year'):
            query += " AND Year_of_Release <= ?"
            params.append(filters['max_year'])
        
        if filters.get('sales_category'):
            query += " AND Sales_Category = ?"
            params.append(filters['sales_category'])
        
        query += " ORDER BY Global_Sales DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.execute_query(query, params)
    
    def get_stats_by_genre(self) -> pd.DataFrame:
        """Statistiques par genre"""
        query = """
            SELECT 
                Genre,
                COUNT(*) as game_count,
                ROUND(SUM(Global_Sales), 2) as total_sales,
                ROUND(AVG(Global_Sales), 2) as avg_sales,
                ROUND(MAX(Global_Sales), 2) as max_sales,
                ROUND(AVG(Critic_Score), 1) as avg_critic_score,
                ROUND(SUM(Global_Sales) * 100.0 / (SELECT SUM(Global_Sales) FROM games), 2) as market_share_percent
            FROM games
            WHERE Genre IS NOT NULL
            GROUP BY Genre
            ORDER BY total_sales DESC
        """
        return self.execute_query(query)
    
    def get_stats_by_publisher(self, min_games: int = 5) -> pd.DataFrame:
        """Statistiques par éditeur"""
        query = """
            SELECT 
                Publisher,
                COUNT(*) as games_released,
                ROUND(SUM(Global_Sales), 2) as total_sales,
                ROUND(AVG(Global_Sales), 2) as avg_sales_per_game,
                ROUND(AVG(Critic_Score), 1) as avg_critic_score,
                COUNT(DISTINCT Genre) as unique_genres,
                SUM(CASE WHEN Sales_Category IN ('Blockbuster', 'Mega-Blockbuster') THEN 1 ELSE 0 END) as blockbuster_count
            FROM games
            WHERE Publisher IS NOT NULL
            GROUP BY Publisher
            HAVING COUNT(*) >= ?
            ORDER BY total_sales DESC
        """
        return self.execute_query(query, [min_games])
    
    def get_time_series(self) -> pd.DataFrame:
        """Analyse temporelle"""
        query = """
            SELECT 
                Year_of_Release as year,
                COUNT(*) as games_released,
                ROUND(SUM(Global_Sales), 2) as total_sales,
                ROUND(AVG(Global_Sales), 2) as avg_sales,
                ROUND(AVG(Critic_Score), 1) as avg_critic_score,
                FIRST(Name ORDER BY Global_Sales DESC) as top_game,
                ROUND(MAX(Global_Sales), 2) as top_sales
            FROM games
            WHERE Year_of_Release BETWEEN 1980 AND 2024
            GROUP BY Year_of_Release
            ORDER BY year
        """
        return self.execute_query(query)
    
    def search_games_sql(self, search_term: str, limit: int = 20) -> pd.DataFrame:
        """Recherche basique avec SQL LIKE"""
        query = """
            SELECT * FROM games 
            WHERE Name LIKE ? 
            ORDER BY Global_Sales DESC 
            LIMIT ?
        """
        return self.execute_query(query, [f"%{search_term}%", limit])
    
    def get_total_count(self, filters: Dict = None) -> int:
        """Compte le nombre total de jeux avec filtres"""
        query = "SELECT COUNT(*) as count FROM games WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('genre'):
                query += " AND Genre = ?"
                params.append(filters['genre'])
            if filters.get('platform'):
                query += " AND Platform = ?"
                params.append(filters['platform'])
        
        result = self.execute_query(query, params)
        return result.iloc[0]['count'] if not result.empty else 0

# Instance globale pour réutilisation
db_manager = DatabaseManager()