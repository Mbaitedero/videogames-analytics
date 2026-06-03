"""
run_project.py — Lance le projet videogames-analytics dans l'ordre recommandé :
  1. Pipeline de données (data_cleaner → duckdb_queries → web_scraper)
  2. API FastAPI  (uvicorn api.main:app --reload)
  3. Dashboard Streamlit (streamlit run dashboard/app.py)

Usage :
  py run_project.py              # tout lancer
  py run_project.py --pipeline   # pipeline seulement
  py run_project.py --api        # API seulement
  py run_project.py --dashboard  # dashboard seulement
  py run_project.py --skip-pipeline  # API + dashboard sans pipeline
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

PYTHON = sys.executable
RAW_CSV = Path("data/raw/video_games_sales.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_step(label: str, cmd: list, check: bool = True) -> bool:
    print(f"\n{'='*60}")
    print(f"▶   {label}")
    print(f"   Commande : {' '.join(cmd)}")
    print('='*60)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"⚠️  '{label}' a terminé avec le code {result.returncode}")
        if check:
            print("   Arrêt du script.")
            sys.exit(result.returncode)
        return False
    print(f"✅ '{label}' terminé avec succès.")
    return True


def start_background(label: str, cmd: list) -> subprocess.Popen:
    print(f"\n{'='*60}")
    print(f"🚀 Lancement en arrière-plan : {label}")
    print(f"   Commande : {' '.join(cmd)}")
    print('='*60)
    return subprocess.Popen(cmd)


# ---------------------------------------------------------------------------
# Étapes
# ---------------------------------------------------------------------------

def run_pipeline():
    print("\n📦 ÉTAPE 1 — Pipeline de données")

    # Vérification du CSV avant de lancer
    if not RAW_CSV.exists():
        print(f"\n❌ Fichier CSV introuvable : {RAW_CSV}")
        print("   👉 Télécharge le dataset sur Kaggle :")
        print("      https://www.kaggle.com/datasets/gregorut/videogamesales")
        print(f"   👉 Place le fichier ici : {RAW_CSV.resolve()}")
        print("\n   Tu peux relancer ensuite avec :")
        print("      py run_project.py --pipeline")
        print("   Ou lancer directement l'API + dashboard (sans pipeline) :")
        print("      py run_project.py --skip-pipeline")
        sys.exit(1)

    run_step("DataCleaner",    [PYTHON, "-m", "scripts.data_cleaner"])
    run_step("DuckDB queries", [PYTHON, "-m", "scripts.duckdb_queries"])
    run_step("Web scraper",    [PYTHON, "-m", "scripts.web_scraper"], check=False)  # optionnel


def run_api() -> subprocess.Popen:
    print("\n🌐 ÉTAPE 2 — API FastAPI")
    # Changement du host à 127.0.0.1 pour stabiliser les connexions Windows locales
    proc = start_background(
        "uvicorn api.main:app --reload",
        ["uvicorn", "api.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
    )
    # Augmentation du temps pour laisser DuckDB respirer au démarrage
    print("   ⏳ Attente de l'initialisation complète de l'API (6 s)...")
    time.sleep(6)
    print("   API accessible sur  : http://127.0.0.1:8000")
    print("   Documentation       : http://127.0.0.1:8000/docs")
    return proc


def run_dashboard() -> subprocess.Popen:
    print("\n📊 ÉTAPE 3 — Dashboard Streamlit")
    proc = start_background(
        "streamlit run dashboard/app.py",
        ["streamlit", "run", "dashboard/app.py"],
    )
    print("   Dashboard accessible sur : http://localhost:8501")
    return proc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lance le projet videogames-analytics")
    parser.add_argument("--pipeline",      action="store_true", help="Pipeline de données seulement")
    parser.add_argument("--api",           action="store_true", help="API FastAPI seulement")
    parser.add_argument("--dashboard",     action="store_true", help="Dashboard Streamlit seulement")
    parser.add_argument("--skip-pipeline", action="store_true", help="API + dashboard sans pipeline")
    parser.add_argument("--capture", action="store_true", help="Capturer le dashboard en images après lancement")
    args = parser.parse_args()

    run_all = not any([args.pipeline, args.api, args.dashboard, args.skip_pipeline])

    processes = []

    try:
        if args.pipeline or run_all:
            run_pipeline()

        if args.api or args.dashboard or args.skip_pipeline or run_all:
            if args.api or args.skip_pipeline or run_all:
                processes.append(run_api())
            if args.dashboard or args.skip_pipeline or run_all:
                processes.append(run_dashboard())

        if args.capture:
            print("\n📸 Capture du dashboard en cours...")
            run_step("Capture dashboard", [PYTHON, "-m", "scripts.capture_dashboard", "--no-open"], check=False)

        if processes:
            print("\n✅ Tous les services sont lancés.")
            print("   Appuie sur Ctrl+C pour tout arrêter.\n")
            for p in processes:
                if p:
                    p.wait()

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé — fermeture des services...")
        for p in processes:
            if p:
                p.terminate()
        print("   Services arrêtés. Au revoir !")
        sys.exit(0)


if __name__ == "__main__":
    main()