import duckdb
from pathlib import Path


PROJECT_ROOT = Path('.')
DB_PATH = PROJECT_ROOT / 'data' / 'videogames.db'
PARQUET_PATH = PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.parquet'


class DuckDBAnalytics:

    def __init__(self, db_path: Path = DB_PATH, parquet_path: Path = PARQUET_PATH):
        self.db_path = db_path
        self.parquet_path = parquet_path
        self.conn = duckdb.connect(str(self.db_path))

        # Utiliser des slashes forward (compatible Windows + DuckDB)
        parquet_str = str(self.parquet_path).replace('\\', '/')
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE games AS 
            SELECT * FROM read_parquet('{parquet_str}')
        """)
        count = self.conn.execute('SELECT COUNT(*) FROM games').fetchone()[0]
        print(f"✅ Table 'games' créée avec {count:,} lignes")

    def close(self):
        self.conn.close()
        print(f"\n✅ Base sauvegardée : {self.db_path}")

    def get_sales_by_genre(self):
        print("📊 Statistiques par Genre :")
        return self.conn.execute("""
            SELECT 
                Genre,
                COUNT(*) as nb_games,
                ROUND(SUM(Global_Sales), 2) as total_sales,
                ROUND(AVG(Global_Sales), 2) as avg_sales
            FROM games
            GROUP BY Genre
            ORDER BY total_sales DESC
        """).fetchdf()

    def get_top_games(self):
        print("🏆 Top 10 jeux par ventes globales :")
        return self.conn.execute("""
            SELECT Name, Platform, Genre, Global_Sales
            FROM games
            ORDER BY Global_Sales DESC
            LIMIT 10
        """).fetchdf()

    def get_publisher_analysis(self, min_games: int = 5):
        print(f"📊 Analyse des Publishers avec au moins {min_games} jeux...")
        return self.conn.execute(f"""
            SELECT 
                Publisher,
                COUNT(*) as games_released,
                ROUND(SUM(Global_Sales), 2) as total_sales,
                ROUND(AVG(Global_Sales), 2) as avg_sales_per_game,
                COUNT(DISTINCT Genre) as unique_genres,
                SUM(CASE WHEN Sales_Category = 'Blockbuster' THEN 1 ELSE 0 END) as blockbuster_count
            FROM games
            WHERE Publisher IS NOT NULL
            GROUP BY Publisher
            HAVING COUNT(*) >= {min_games}
            ORDER BY total_sales DESC
        """).fetchdf()

    def get_time_series_analysis(self):
        print("📈 Analyse temporelle des ventes...")
        return self.conn.execute("""
            WITH ranked AS (
                SELECT 
                    Genre,
                    Name,
                    Global_Sales,
                    ROW_NUMBER() OVER (
                        PARTITION BY Genre 
                        ORDER BY Global_Sales DESC
                    ) as rank
                FROM games
            )
            SELECT Genre, rank, Name, Global_Sales
            FROM ranked
            WHERE rank <= 3
            ORDER BY Genre, rank
        """).fetchdf()


if __name__ == '__main__':
    analytics = DuckDBAnalytics()
    print(analytics.get_top_games())
    print(analytics.get_sales_by_genre())
    print(analytics.get_time_series_analysis())
    print(analytics.get_publisher_analysis())
    analytics.close()