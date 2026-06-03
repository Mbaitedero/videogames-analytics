from elasticsearch import Elasticsearch, helpers
import pandas as pd
from typing import List, Dict


class ElasticsearchIndexer:

    def __init__(self, host: str = "localhost", port: int = 9200):
        self.host = host
        self.port = port
        self.es = Elasticsearch(f"http://{host}:{port}")

        if not self.es.ping():
            raise ConnectionError(f"❌ Elasticsearch non disponible sur {host}:{port}")

        print(f"✅ Connecté à Elasticsearch ({host}:{port})")

    def index_games(self, df: pd.DataFrame, index_name: str = "videogames") -> int:
        """
        Indexe les jeux dans Elasticsearch.
        Supprime et recrée l'index avec un mapping adapté avant l'indexation.
        """
        # Supprimer l'index s'il existe
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
            print(f"   Index '{index_name}' supprimé")

        # Créer l'index avec mapping
        mapping = {
            "mappings": {
                "properties": {
                    "Name": {"type": "text", "analyzer": "standard"},
                    "Platform": {"type": "keyword"},
                    "Genre": {"type": "keyword"},
                    "Publisher": {"type": "keyword"},
                    "Year_of_Release": {"type": "integer"},
                    "Global_Sales": {"type": "float"},
                    "Critic_Score": {"type": "float"},
                    "Sales_Category": {"type": "keyword"},
                }
            }
        }
        self.es.indices.create(index=index_name, body=mapping)
        print(f"   Index '{index_name}' créé")

        # Préparer les documents (remplacer NaN par None)
        records = df.where(pd.notnull(df), None).to_dict('records')

        # Bulk indexation
        actions = [
            {"_index": index_name, "_source": record}
            for record in records
        ]

        success, errors = helpers.bulk(self.es, actions, raise_on_error=False)

        print(f"✅ {success} documents indexés")
        if errors:
            print(f"⚠️ {len(errors)} erreurs")

        return success

    def search_games_advanced(self, q: str, size: int = 10, filters: Dict = None) -> List[Dict]:
        """
        Recherche des jeux par nom (fuzzy search) avec filtres optionnels.

        Args:
            q: Terme de recherche (fuzzy sur le champ Name).
            size: Nombre de résultats à retourner.
            filters: Dictionnaire de filtres supplémentaires (ex: {"Genre": "Action"}).
        """
        must_clauses = [
            {
                "match": {
                    "Name": {
                        "query": q,
                        "fuzziness": "AUTO",
                    }
                }
            }
        ]

        filter_clauses = []
        if filters:
            for field, value in filters.items():
                filter_clauses.append({"term": {field: value}})

        query = {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        }

        response = self.es.search(index="videogames", query=query, size=size)

        results = []
        for hit in response['hits']['hits']:
            results.append({
                'score': hit['_score'],
                **hit['_source'],
            })

        return results


if __name__ == '__main__':
    try:
        indexer = ElasticsearchIndexer(host="localhost", port=9200)

        # Charger et indexer
        df = pd.read_parquet('videogames-analytics/data/processed/games_cleaned.parquet')
        indexer.index_games(df)

        # Recherche avec faute de frappe
        print("\n🔍 Recherche 'Final Fantasi' (avec faute) :")
        results = indexer.search_games_advanced(q="Final Fantasi", size=5)
        for r in results:
            print(f"   {r['Name']} ({r['Platform']}) - Score: {r['score']:.2f}")

        # Recherche avec filtre genre
        print("\n🔍 Recherche 'Mario' filtré sur Genre=Platform :")
        results_filtered = indexer.search_games_advanced(
            q="Mario", size=5, filters={"Genre": "Platform"}
        )
        for r in results_filtered:
            print(f"   {r['Name']} ({r['Platform']}) - Score: {r['score']:.2f}")

    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        print("   Assure-toi qu'Elasticsearch est lancé sur localhost:9200")