"""Tests unitaires pour le module de web scraping, nettoyage et indexation ES"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock


# ---------------------------------------------------------------------------
# TestWebScraper
# ---------------------------------------------------------------------------

class TestWebScraper:
    """Tests pour WebScraper — scrape() mocké via requests.get."""

    @patch('scripts.web_scraper.requests.get')
    def test_scrape_returns_dataframe(self, mock_get):
        """scrape() doit retourner un DataFrame non vide sur une réponse 200."""
        from scripts.web_scraper import WebScraper

        html = """
        <html><body>
          <table>
            <tr><th>Name</th><th>Platform</th><th>Global_Sales</th></tr>
            <tr><td>Zelda</td><td>Switch</td><td>10.5</td></tr>
          </table>
        </body></html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = Mock()
        # requests.get() retourne directement mock_response
        mock_get.return_value = mock_response

        scraper = WebScraper()
        df = scraper.scrape_bestselling_games()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    @patch('scripts.web_scraper.requests.get')
    def test_scrape_handles_http_error(self, mock_get):
        """scrape() doit gérer proprement une erreur HTTP (ex. 404)."""
        from scripts.web_scraper import WebScraper
        import requests

        mock_get.side_effect = requests.HTTPError("404 Not Found")

        scraper = WebScraper()
        result = scraper.scrape_bestselling_games()
        assert result is None or isinstance(result, pd.DataFrame)
        
    @patch('scripts.web_scraper.requests.get')
    def test_scrape_columns_present(self, mock_get):
        """Le DataFrame renvoyé doit contenir les colonnes minimales attendues."""
        from scripts.web_scraper import WebScraper

        html = """
        <html><body>
          <table>
            <tr><th>Name</th><th>Platform</th><th>Global_Sales</th><th>Year_of_Release</th></tr>
            <tr><td>Mario</td><td>Wii</td><td>5.0</td><td>2010</td></tr>
          </table>
        </body></html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scraper = WebScraper()
        df = scraper.scrape_bestselling_games()

        required_cols = {'Name', 'Platform', 'Global_Sales'}
        assert required_cols.issubset(set(df.columns))


# ---------------------------------------------------------------------------
# TestDataCleaner
# ---------------------------------------------------------------------------

inputPath = "videogames-analytics/data/raw/video_games_sales.csv"
outputPath = "videogames-analytics/data/processed/games_cleaned.parquet"


class TestDataCleaner:
    """Tests pour DataCleaner — clean_data() testé avec de vrais DataFrames."""

    @pytest.fixture
    def raw_df(self):
        """DataFrame brut représentatif avec doublons et valeurs manquantes."""
        return pd.DataFrame({
            'Name':            ['Game1', 'Game2', 'Game1', 'Game3'],
            'Platform':        ['PS4',   'Xbox',  'PS4',   'PC'],
            'Year_of_Release': [2020,    np.nan,  2020,    2019],
            'Genre':           ['Action','RPG',   'Action','Sport'],
            'Publisher':       ['Pub1',  'Pub2',  'Pub1',  'Pub3'],
            'Global_Sales':    [1.8,     4.0,     np.nan,  2.2],
            'Critic_Score':    [85,      np.nan,  85,      70],
            'User_Score':      [8.5,     9.0,     8.5,     7.0],
        })

    def test_clean_removes_duplicates(self, raw_df):
        """clean_data() doit supprimer les doublons (Game1 PS4 apparaît deux fois)."""
        from scripts.data_cleaner import DataCleaner

        cleaner = DataCleaner(input_path=inputPath, output_path=outputPath)
        cleaned = cleaner.clean_data(raw_df)

        assert cleaned.duplicated(subset=['Name', 'Platform']).sum() == 0

    def test_clean_no_all_null_rows(self, raw_df):
        """clean_data() ne doit pas conserver de lignes entièrement vides."""
        from scripts.data_cleaner import DataCleaner

        cleaner = DataCleaner(input_path=inputPath, output_path=outputPath)
        cleaned = cleaner.clean_data(raw_df)

        assert cleaned.isnull().all(axis=1).sum() == 0

    def test_clean_year_dtype(self, raw_df):
        """Après clean_data(), Year_of_Release doit être un entier (ou nullable int)."""
        from scripts.data_cleaner import DataCleaner

        cleaner = DataCleaner(input_path=inputPath, output_path=outputPath)
        cleaned = cleaner.clean_data(raw_df)

        assert cleaned['Year_of_Release'].dtype in [
            'int64', 'int32', 'Int64', 'Int32', np.dtype('int64'),
        ]

    def test_clean_global_sales_positive(self, raw_df):
        """Toutes les valeurs de Global_Sales conservées doivent être positives."""
        from scripts.data_cleaner import DataCleaner

        cleaner = DataCleaner(input_path=inputPath, output_path=outputPath)
        cleaned = cleaner.clean_data(raw_df)
        sales = cleaned['Global_Sales'].dropna()

        assert (sales >= 0).all()

    def test_clean_output_is_dataframe(self, raw_df):
        """clean_data() doit retourner un pd.DataFrame."""
        from scripts.data_cleaner import DataCleaner

        cleaner = DataCleaner(input_path=inputPath, output_path=outputPath)
        result = cleaner.clean_data(raw_df)

        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# TestElasticsearchIndexer
# ---------------------------------------------------------------------------

class TestElasticsearchIndexer:
    """Tests pour ElasticsearchIndexer avec connexion Elasticsearch simulée."""

    @patch('scripts.elasticsearch_indexer.Elasticsearch')
    def test_init_success(self, mock_es_cls):
        """__init__ doit réussir si es.ping() renvoie True."""
        from scripts.elasticsearch_indexer import ElasticsearchIndexer

        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es_cls.return_value = mock_es

        indexer = ElasticsearchIndexer(host="localhost", port=9200)
        assert indexer is not None

    @patch('scripts.elasticsearch_indexer.Elasticsearch')
    def test_init_raises_on_unavailable(self, mock_es_cls):
        """__init__ doit lever ConnectionError si ping() renvoie False."""
        from scripts.elasticsearch_indexer import ElasticsearchIndexer

        mock_es = MagicMock()
        mock_es.ping.return_value = False
        mock_es_cls.return_value = mock_es

        with pytest.raises(ConnectionError):
            ElasticsearchIndexer(host="invalid-host", port=9999)

    @patch('scripts.elasticsearch_indexer.helpers')
    @patch('scripts.elasticsearch_indexer.Elasticsearch')
    def test_index_games_returns_count(self, mock_es_cls, mock_helpers):
        """index_games() doit retourner le nombre de documents indexés."""
        from scripts.elasticsearch_indexer import ElasticsearchIndexer

        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es.indices.exists.return_value = False
        mock_es_cls.return_value = mock_es
        mock_helpers.bulk.return_value = (5, [])

        df = pd.DataFrame({
            'Name': [f'Game{i}' for i in range(5)],
            'Platform': ['PS4'] * 5,
            'Genre': ['Action'] * 5,
            'Publisher': ['Pub'] * 5,
            'Year_of_Release': [2020] * 5,
            'Global_Sales': [1.0] * 5,
            'Critic_Score': [80.0] * 5,
            'Sales_Category': ['Medium'] * 5,
        })

        indexer = ElasticsearchIndexer()
        result = indexer.index_games(df)

        assert result == 5
        mock_helpers.bulk.assert_called_once()

    @patch('scripts.elasticsearch_indexer.Elasticsearch')
    def test_search_games_advanced_calls_es_search(self, mock_es_cls):
        """search_games_advanced() doit appeler es.search et retourner une liste."""
        from scripts.elasticsearch_indexer import ElasticsearchIndexer

        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es.search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_score': 1.5,
                        '_source': {
                            'Name': 'Final Fantasy VII',
                            'Platform': 'PS1',
                            'Genre': 'RPG',
                            'Global_Sales': 9.7,
                        },
                    }
                ]
            }
        }
        mock_es_cls.return_value = mock_es

        indexer = ElasticsearchIndexer()
        results = indexer.search_games_advanced(q="Final Fantasi", size=5)

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]['Name'] == 'Final Fantasy VII'

    @patch('scripts.elasticsearch_indexer.Elasticsearch')
    def test_search_games_advanced_with_filters(self, mock_es_cls):
        """search_games_advanced() doit appeler es.search avec les filtres passés."""
        from scripts.elasticsearch_indexer import ElasticsearchIndexer

        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es.search.return_value = {'hits': {'hits': []}}
        mock_es_cls.return_value = mock_es

        indexer = ElasticsearchIndexer()
        results = indexer.search_games_advanced(
            q="Mario", size=5, filters={"Genre": "Platform"}
        )

        mock_es.search.assert_called_once()
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])