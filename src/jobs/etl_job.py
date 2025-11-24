from src.config.spark_config import create_spark_session
from pyspark.sql.functions import col

import os


def run_etl():
    """
    Runs the ETL job using Spark.
    """
    spark = create_spark_session()

    # IMPORTANT: Force credentials
    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    hadoop_conf.set("fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")

    print("=== Reading raw JSONL from S3 bucket ===")

    df_raw = spark.read.json("s3a://stream-data-raghu/raw/stream_raw.jsonl")

    print("Schema:")
    df_raw.printSchema()

    print("=== Selecting key fields ===")
    df_selected = df_raw.select(
        "order_id",
        "warehouse",
        "customer_zip",
        "weight_kg",
        "carrier",
        "event_time"
    )

    print("=== Cleaning missing values ===")
    df_clean = df_selected.fillna({
        "warehouse": "UNKNOWN",
        "customer_zip": "00000",
        "carrier": "UNKNOWN"
    })

    print("=== Showing Cleaned Sample ===")
    df_clean.show(10)

    print("=== Writing cleaned data back to S3 (processed zone) ===")
    output_path = "s3a://stream-data-raghu/processed/cleaned_data/"
    df_clean.write.mode("overwrite").parquet(output_path)
    print(f"Cleaned data written to: {output_path}")

    spark.stop()







   
   