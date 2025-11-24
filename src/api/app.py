from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.api.predict_utils import predict_delivery_days    


app = FastAPI(
    tittle = "Delivery Time Prediction API",
    description = "Predict delivery days using ML model + engineered features",
    version = "1.0"
)

# Input Schema
class DeliveryInput(BaseModel):
    order_id: Optional[str]
    warehouse: str
    customer_zip: str
    weight_kg: float
    carrier: str
    event_time: str   # ISO format timestamp: "2025-11-18T12:34:00"

# Root endpoint
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Delivery prediction API is ready."
    }

# Prediction endpoint
@app.post("/predict")
def predict(data: DeliveryInput):
    """
    Receive JSON → run ML pipeline → return predicted delivery_days.
    """
    prediction = predict_delivery_days(data.dict())

    return {
        "order_id": data.order_id,
        "predicted_delivery_days": round(prediction, 2)
    }