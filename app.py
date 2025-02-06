from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, avg, row_number, min, first, udf
from pyspark.sql.types import StringType
import re
import sys
import os

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def get_track_id(url: str):
    url_parts = url.split("/")
    return url_parts[-1]


trackUdf = udf(lambda m: get_track_id(m), StringType())


year = sys.argv[1]
month = sys.argv[2]
spark = SparkSession.builder.appName("SpotifyDataSet").config("spark.jars", "/app/mysql-connector-j-9.1.0.jar").master("local[*]").getOrCreate()
category = "top200"
df = spark.read.option("encoding", "windows-1256").parquet("/app/charts.parquet")
df_filtered = df.filter(df["chart"] == category)
df_filtered = df_filtered.filter(
    (df["date"].substr(1, 4) == str(year)) & (df["date"].substr(6, 2) == str(month).zfill(2))
)
df_average_streams = df_filtered.groupBy("region", "artist").agg(
    avg("streams").alias("avg_streams")
)
window_spec_avg = Window.partitionBy("region").orderBy(col("avg_streams").desc())
df_top_artist = df_average_streams.withColumn("rank", row_number().over(window_spec_avg)).filter(col("rank") == 1)
df_filtered_top_artist = df_filtered.join(
    df_top_artist.select("region", "artist"), on=["region", "artist"], how="inner"
)
window_spec_date = Window.partitionBy("region", "artist").orderBy(col("rank"), col("date"))
df_with_earliest_date = df_filtered_top_artist.withColumn("row_num", row_number().over(window_spec_date)).filter(
    col("row_num") == 1
)
def extract_track_id(url):
    match = re.search(r"track/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None
extract_track_id_udf = udf(extract_track_id, StringType())
df_with_earliest_date = df_with_earliest_date.withColumn("track_id", extract_track_id_udf(col("url")))
df_min_rank = df_with_earliest_date.groupBy("region", "artist").agg(
    min("rank").alias("min_rank"),
    first("title").alias("best_title"),
    first("date").alias("best_date"),
    first("track_id").alias("track_id")
)
df_final = df_min_rank.join(df_top_artist, on=["region", "artist"], how="inner")

df_final.show()

df_final.write.format("jdbc").options(
    url=os.getenv("MYSQL_URL"),
    driver=os.getenv("MYSQL_DRIVER"),
    dbtable=os.getenv("MYSQL_TABLE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("PASSWORD") 
).mode("append").save()


spark.stop()
