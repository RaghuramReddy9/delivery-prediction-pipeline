import joblib
import pandas as pd
import numpy as np
import os

# Load model at import time (fast)
MODEL_PATH = os.path.join(os.path.dirname(__file__),"..", "..", "delivery_model.joblib")
model = joblib.load(MODEL_PATH)

def prepare_features(input_dict):
    """
    Convert incoming JSON into model-ready dataframe.
    """
    df = pd.DataFrame([input_dict])

    # Feature engineering: same as training
    df["event_ts"] = pd.to_datetime(df["event_time"])
    df["event_hour"] = df["event_ts"].dt.hour
    df["event_dayofweek"] = df["event_ts"].dt.dayofweek

    # Weight bucket
    df["weight_bucket"] = pd.cut(
        df["weight_kg"],
        bins=[0, 2, 5, 10],
        labels=["light", "medium", "heavy"],
        include_lowest=True
    )

    # Distance proxy
    df["distance_proxy"] = df["customer_zip"].astype(int) % 100

    # Binary features
    df["is_heavy"] = (df["weight_kg"] > 5).astype(int)
    df["is_east_coast"] = df["warehouse"].isin(["NEW_YORK", "MIAMI"]).astype(int)

    # Encoding (must match training)
    carrier_map = {"UPS": 0, "FEDEX": 1, "DHL": 2}
    warehouse_map = {"NEW_YORK": 0, "LOS_ANGELES": 1, "MIAMI": 2, "SAN_JOSE": 3}

    df["carrier_encoded"] = df["carrier"].map(carrier_map)
    df["warehouse_encoded"] = df["warehouse"].map(warehouse_map)

    # Select features
    feature_cols = [
        "weight_kg",
        "distance_proxy",
        "is_heavy",
        "is_east_coast",
        "carrier_encoded",
        "warehouse_encoded",
        "event_hour",
        "event_dayofweek"
    ]

    return df[feature_cols]

def predict_delivery_days(input_dict):
    """
    Run full preprocessing + model prediction.
    """
    features = prepare_features(input_dict)
    prediction = model.predict(features)[0]
    return float(prediction)