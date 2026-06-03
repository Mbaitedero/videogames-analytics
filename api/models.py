"""Modèles Pydantic pour l'API - Validation des données"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GameBase(BaseModel):
    """Modèle de base pour un jeu vidéo"""
    name: str = Field(..., description="Nom du jeu")
    platform: str = Field(..., description="Plateforme")
    genre: Optional[str] = Field(None, description="Genre")
    publisher: Optional[str] = Field(None, description="Éditeur")
    year: int = Field(..., ge=1980, le=2024, description="Année de sortie")
    global_sales: float = Field(..., ge=0, description="Ventes mondiales (millions)")
    critic_score: Optional[float] = Field(None, ge=0, le=100, description="Score Metacritic")
    user_score: Optional[float] = Field(None, ge=0, le=10, description="Score utilisateur")
    sales_category: str = Field(..., description="Catégorie de ventes")

class GameResponse(BaseModel):
    name: str = Field(alias="Name")
    platform: str = Field(alias="Platform")
    genre: Optional[str] = Field(None, alias="Genre")
    publisher: Optional[str] = Field(None, alias="Publisher")
    year: Optional[int] = Field(None, alias="Year_of_Release")
    global_sales: float = Field(alias="Global_Sales")
    critic_score: Optional[float] = Field(None, alias="Critic_Score")
    user_score: Optional[float] = Field(None, alias="User_Score")
    sales_category: Optional[str] = Field(None, alias="Sales_Category")

    class Config:
        from_attributes = True
        populate_by_name = True

class GameListResponse(BaseModel):
    """Liste paginée de jeux"""
    total: int = Field(..., description="Nombre total de résultats")
    limit: int = Field(..., description="Limite demandée")
    offset: int = Field(..., description="Offset demandé")
    games: List[GameResponse] = Field(..., description="Liste des jeux")

class SearchRequest(BaseModel):
    """Requête de recherche"""
    query: str = Field(..., min_length=1, max_length=100, description="Terme de recherche")
    genre: Optional[str] = Field(None, description="Filtrer par genre")
    platform: Optional[str] = Field(None, description="Filtrer par plateforme")
    min_sales: Optional[float] = Field(None, ge=0, description="Ventes minimum")
    max_sales: Optional[float] = Field(None, ge=0, description="Ventes maximum")
    min_year: Optional[int] = Field(None, ge=1980, le=2024, description="Année minimum")
    max_year: Optional[int] = Field(None, ge=1980, le=2024, description="Année maximum")
    limit: int = Field(10, ge=1, le=100, description="Nombre de résultats")

class SearchResponse(BaseModel):
    """Réponse de recherche"""
    query: str
    total_results: int
    results: List[GameResponse]
    suggestions: List[str] = Field(default_factory=list, description="Suggestions de recherche")

class StatsByGenre(BaseModel):
    """Statistiques par genre"""
    genre: str
    game_count: int
    total_sales: float
    avg_sales: float
    max_sales: float
    avg_critic_score: Optional[float]
    market_share_percent: float

class StatsByPublisher(BaseModel):
    """Statistiques par éditeur"""
    publisher: str
    games_released: int
    total_sales: float
    avg_sales_per_game: float
    avg_critic_score: Optional[float]
    unique_genres: int
    blockbuster_count: int

class TimeSeriesPoint(BaseModel):
    """Point de série temporelle"""
    year: int
    games_released: int
    total_sales: float
    avg_sales: float
    avg_critic_score: Optional[float]
    top_game: str
    top_sales: float

class HealthResponse(BaseModel):
    """Réponse de santé de l'API"""
    status: str
    version: str
    timestamp: datetime
    database_connected: bool
    elasticsearch_connected: bool