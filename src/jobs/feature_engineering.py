from src.config.spark_config import create_spark_session
import pyspark.sql.functions as F


def run_feature_engineering():
    """
    Runs the Feature Engineering job using Spark.
    Transforms cleaned data → analytics dataset.
    """

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    print("=== Reading cleaned data from S3 ===")
    input_path = "s3a://stream-data-raghu/processed/cleaned_data/"
    df = spark.read.parquet(input_path)

    # TIMESTAMP FEATURES
    print("=== Extracting timestamp features ===")
    df = (
        df.withColumn("event_ts", F.to_timestamp("event_time"))
          .withColumn("event_date", F.to_date("event_ts"))
          .withColumn("event_hour", F.hour("event_ts"))
          .withColumn("event_dayofweek", F.dayofweek("event_ts"))
    )

    # WEIGHT BUCKETS
    print("=== Creating weight buckets ===")
    df = df.withColumn(
        "weight_bucket",
        F.when(F.col("weight_kg") < 1, "very_light")
         .when(F.col("weight_kg") < 5, "light")
         .when(F.col("weight_kg") < 10, "medium")
         .otherwise("heavy")
    )

    # DISTANCE PROXY FEATURE
    print("=== Creating distance proxy feature ===")
    # proxy distance based on zip code difference
    df = df.withColumn(
        "distance_proxy",
        F.abs(F.col("customer_zip").cast("int") - F.lit(95000))
    )

    # BINARY FEATURES (LABEL ENGINEERING)
    print("=== Creating binary features ===")
    df = df.withColumn("is_heavy", F.col("weight_kg") > 7)
    df = df.withColumn("is_east_coast", F.col("warehouse").isin("NEW_YORK", "MIAMI"))

    # CATEGORICAL ENCODING
    print("=== Encoding categorical variables ===")
    df = (
        df.withColumn("carrier_encoded", F.hash("carrier"))
          .withColumn("warehouse_encoded", F.hash("warehouse"))
    )

    # WRITE OUTPUT TO S3 (ANALYTICS ZONE)
    output_path = "s3a://stream-data-raghu/analytics/features/"

    print(f"=== Writing analytics dataset to {output_path} ===")
    df.write.mode("overwrite").parquet(output_path)

    print("=== Feature Engineering Complete ===")

    spark.stop()

