from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, when, rand, expr)
from src.config.spark_config import create_spark_session   


def run_label_generation():
    """
    Run label generation job to create labels for the dataset.
    """

    spark = create_spark_session()

    print("=== Reading engineered features from S3 ===")
    input_path = "s3a://stream-data-raghu/analytics/features/"
    df = spark.read.parquet(input_path)

    print("=== Creating realistic delivery_time label ===")

    ## Simulate Components ##

    # weight effect (heavier = slower)
    df = df.withColumn(
        "w_effect",
        when(col("weight_kg") < 2, 0.5)
        .when(col("weight_kg") < 5, 1.0)
        .when(col("weight_kg") < 8, 1.5)
        .otherwise(2.0)
    )

    # Carrier effect (based on relative delivery speed)
    df = df.withColumn(
        "c_effect",
        when(col("carrier") == "FEDEX", 1.0)
        .when(col("carrier") == "UPS", 1.2)
        .when(col("carrier") == "DHL", 1.4)
        .otherwise(1.3)
    )

    # Distance proxy effect
    df = df.withColumn(
        "d_effect",
        col("distance_proxy") * 1.3
    )

    # Day-of-week effect (weekends slower)
    df = df.withColumn(
        "dow_effect",
        when(col("event_dayofweek").isin(5, 6), 0.8)
        .otherwise(0.4)
    )

    # Random noise for realism
    df = df.withColumn(
        "noise",
        rand() * 0.7
    )

    ## FINAL LABEL 
    df = df.withColumn(
        "delivery_days",
        (
            expr("1.5") +
            col("w_effect") +
            col("c_effect") +
            col("d_effect") +
            col("dow_effect") +
            col("noise")
        )
    )

    # Make it clean
    df = df.drop("w_effect", "c_effect", "d_effect", "dow_effect", "noise")

    print("=== Saving labeled dataset to S3 ===")

    output_path = "s3a://stream-data-raghu/model/features_labeled/"
    df.write.mode("overwrite").parquet(output_path)

    print(f"=== Label generation complete! ===")
    print(f"Saved to: {output_path}")

    spark.stop()




