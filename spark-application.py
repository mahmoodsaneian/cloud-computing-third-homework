from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("spark-basic-app").master("local[*]").getOrCreate()

sample_data = [("Mahmood", 22), ("Sina", 53), ("Ghasem", 41)]
columns = ["Name", "Age"]
data_frame = spark.createDataFrame(sample_data, columns)

filtered_data_frame = data_frame.filter(data_frame["Age"] > 30)

print("Filtered data frame")
filtered_data_frame.show()

spark.stop()