import requests
from bs4 import BeautifulSoup
import pandas as pd


class WebScraper:
    def __init__(self):
        pass

    def scrape_bestselling_games(self) -> pd.DataFrame:
        """
        Scrape la liste des jeux les plus vendus depuis Wikipedia.
        Retourne un DataFrame avec les colonnes : Name, Global_Sales, Platform.
        """
        url = "https://en.wikipedia.org/wiki/List_of_best-selling_video_games"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Educational Bot - Data Engineering Bootcamp)'
        }

        print(f"🌐 Récupération de {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"❌ Erreur HTTP : {e}")
            return None
        except requests.RequestException as e:
            print(f"❌ Erreur réseau : {e}")
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        # Cherche wikitable, sinon fallback sur n'importe quel <table>
        table = soup.find('table', {'class': 'wikitable'}) or soup.find('table')

        if not table:
            raise ValueError("❌ Tableau non trouvé sur la page")

        games = []
        rows = table.find_all('tr')[1:11]  # Skip header, prendre 10 lignes

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                games.append({
                    'Name': cells[0].get_text(strip=True),
                    'Global_Sales': cells[1].get_text(strip=True),
                    'Platform': cells[2].get_text(strip=True),
                })

        print(f"✅ {len(games)} jeux extraits")
        return pd.DataFrame(games)


if __name__ == "__main__":
    scraper = WebScraper()
    try:
        df_wiki = scraper.scrape_bestselling_games()
        print("\n🎮 Top 10 jeux les plus vendus (Wikipedia) :")
        print(df_wiki.to_string(index=False))
    except Exception as e:
        print(f"❌ Erreur : {e}")