from scripts.duckdb_queries import DuckDBAnalytics
from scripts.elasticsearch_indexer import ElasticsearchIndexer
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse  # <-- 1. Importation du composant requis
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from loguru import logger
import pandas as pd


# ---------------------------------------------------------------------------
# Modèles Pydantic
# ---------------------------------------------------------------------------

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[Dict[str, Any]]
    suggestions: List[str]


class StatsResponse(BaseModel):
    total_games: int
    total_sales: float
    avg_score: float
    top_genre: str
    top_publisher: str


# ---------------------------------------------------------------------------
# App + instances globales (créées une seule fois)
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Video Games Analytics API",
    description="API pour l'analyse des ventes de jeux vidéo",
    version="1.0.0",
    default_response_class=ORJSONResponse,  # <-- 2. Appliqué globalement à toutes les routes
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance unique — évite de recharger le parquet à chaque requête
_db: DuckDBAnalytics = None
_es: ElasticsearchIndexer = None


@app.on_event("startup")
async def startup_event():
    global _db, _es
    logger.info("API démarrage — chargement DuckDB...")
    _db = DuckDBAnalytics()
    logger.info(f"DuckDB prêt.")
    try:
        _es = ElasticsearchIndexer()
        logger.info("Elasticsearch connecté.")
    except ConnectionError:
        logger.warning("Elasticsearch indisponible — fonctionnalité de recherche désactivée.")
        _es = None


@app.on_event("shutdown")
async def shutdown_event():
    if _db:
        _db.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Video Games Analytics API",
        "version": "1.0.0",
        "endpoints": ["/games", "/games/{name}", "/search", "/stats/genres",
                      "/stats/publishers", "/stats/overview", "/stats/time-series"],
    }


@app.get("/games")
async def get_games(
    genre: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    min_sales: Optional[float] = Query(None),
    publisher: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=20000),
):
    query = "SELECT * FROM games WHERE 1=1"
    params = []

    if genre:
        query += " AND Genre = ?"
        params.append(genre)
    if platform:
        query += " AND Platform = ?"
        params.append(platform)
    if min_sales is not None:
        query += " AND Global_Sales >= ?"
        params.append(min_sales)
    if publisher:
        query += " AND Publisher = ?"
        params.append(publisher)

    query += " ORDER BY Global_Sales DESC LIMIT ?"
    params.append(limit)

    df = _db.conn.execute(query, params).fetchdf()
    
    # ORJSON gère les NaN en les transformant en null, le nettoyage manuel lourd devient optionnel
    return df.to_dict(orient="records")


@app.get("/games/{name}")
async def get_game(name: str):
    df = _db.conn.execute("SELECT * FROM games WHERE Name = ? LIMIT 1", [name]).fetchdf()
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Jeu '{name}' non trouvé")
    return df.iloc[0].to_dict()


@app.get("/search", response_model=SearchResponse)
async def search_games(
    q: str = Query(...),
    size: int = Query(10, ge=1, le=10000),
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    min_sales: Optional[float] = None,
):
    if _es is None:
        raise HTTPException(status_code=503, detail="Elasticsearch indisponible")

    filters: Dict[str, Any] = {}
    if genre:
        filters["Genre"] = genre
    if platform:
        filters["Platform"] = platform
    if min_sales is not None:
        filters["min_sales"] = min_sales

    results = _es.search_games_advanced(q=q, size=size, filters=filters)
    if isinstance(results, tuple):
        results, suggestions = results
    else:
        suggestions = []

    return SearchResponse(query=q, total_results=len(results),
                          results=results, suggestions=suggestions)


@app.get("/stats/genres")
async def stats_by_genre():
    df = _db.get_sales_by_genre()
    return df.to_dict(orient="records")


@app.get("/stats/publishers")
async def stats_by_publisher(limit: int = Query(10, ge=1, le=500)):
    df = _db.get_publisher_analysis()
    return df.head(limit).to_dict(orient="records")


@app.get("/stats/overview", response_model=StatsResponse)
async def stats_overview():
    total_games = _db.conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    total_sales = _db.conn.execute("SELECT SUM(Global_Sales) FROM games").fetchone()[0]

    try:
        avg_score = _db.conn.execute(
            "SELECT AVG(Critic_Score) FROM games WHERE Critic_Score IS NOT NULL"
        ).fetchone()[0]
    except Exception:
        avg_score = None

    top_genre = _db.conn.execute(
        "SELECT Genre FROM games GROUP BY Genre ORDER BY SUM(Global_Sales) DESC LIMIT 1"
    ).fetchone()

    top_publisher = _db.conn.execute(
        "SELECT Publisher FROM games WHERE Publisher IS NOT NULL "
        "GROUP BY Publisher ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()

    return StatsResponse(
        total_games=total_games,
        total_sales=round(total_sales or 0.0, 2),
        avg_score=round(avg_score, 1) if avg_score else 0.0,
        top_genre=top_genre[0] if top_genre else "N/A",
        top_publisher=top_publisher[0] if top_publisher else "N/A",
    )


@app.get("/stats/time-series")
async def time_series_analysis():
    df = _db.get_time_series_analysis()
    return df.to_dict(orient="records")