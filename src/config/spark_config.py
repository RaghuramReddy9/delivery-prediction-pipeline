import os
import sys
from pyspark.sql import SparkSession


def create_spark_session():
    """
    Creates and returns a fully configured SparkSession for:
    - Windows machines
    - S3 read/write using s3a://
    - Using your current virtual environment Python (fixes python3 error)
    """

    spark = (
        SparkSession.builder
        .appName("stream_pipeline")

        # AWS S3 AUTHENTICATION
        .config("spark.hadoop.fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
        .config("spark.hadoop.fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")

        # S3 FILESYSTEM SETTINGS
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.fast.upload", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")

        # WINDOWS PYTHON FIX
        # Spark workers MUST use your venv python
        .config("spark.executorEnv.PYSPARK_PYTHON", sys.executable)
        .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", sys.executable)

        # Optional: reduce logs
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")
    return spark
