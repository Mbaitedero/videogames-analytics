from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pathlib import Path

PROJECT_ROOT = Path('videogames-analytics')

# Créer la session Spark
spark = SparkSession.builder \
    .appName("VideoGamesAnalytics") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print(f"✅ Spark {spark.version} initialisé")

# 1. Charger les données
games_sdf = spark.read.parquet(str(PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.parquet'))
print(f"📊 {games_sdf.count():,} jeux chargés")

# 2. Stats par Publisher
print("\n🏢 Statistiques par Publisher :")
publisher_stats = games_sdf.groupBy("Publisher").agg(
    F.count("*").alias("nb_games"),
    F.round(F.sum("Global_Sales"), 2).alias("total_sales"),
    F.round(F.avg("Critic_Score"), 1).alias("avg_critic"),
    F.countDistinct("Genre").alias("nb_genres")
).orderBy(F.desc("total_sales"))

publisher_stats.show(10)

# 3. Classement par genre avec Window
print("\n🏆 Top 3 jeux par genre :")
window_genre = Window.partitionBy("Genre").orderBy(F.desc("Global_Sales"))

ranked_games = games_sdf.withColumn(
    "rank_in_genre", F.row_number().over(window_genre)
).filter(
    F.col("rank_in_genre") <= 3
).select(
    "Genre", "rank_in_genre", "Name", "Platform", "Global_Sales"
).orderBy("Genre", "rank_in_genre")

ranked_games.show(20)

# 4. Sauvegarder
output_path = PROJECT_ROOT / 'data' / 'processed' / 'publisher_stats'
publisher_stats.write.mode("overwrite").parquet(str(output_path))
print(f"✅ Résultats sauvegardés : {output_path}")

spark.stop()