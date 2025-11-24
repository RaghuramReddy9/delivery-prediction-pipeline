import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import joblib

# Load the labeled dataset
print("=== Loading labeled dataset ===")
df = pd.read_parquet("data_lake/model/features_labeled.parquet")

# Select final engineered features
print("=== Selecting engineered features ===")

FEATURES = [
    "weight_kg",
    "distance_proxy",
    "is_heavy",
    "is_east_coast",
    "carrier_encoded",
    "warehouse_encoded",
    "event_hour",
    "event_dayofweek"
]

TARGET = "delivery_days"

X = df[FEATURES]
y = df[TARGET]

# Train/Test Split
print("=== Splitting dataset (train/test) ===")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define Models
models = {
    "linear_regression": LinearRegression(),
    "decision_tree": DecisionTreeRegressor(max_depth=6),
    "random_forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
}

results = {}

# Train + Evaluate each model
print("=== Training models ===")
for name, model in models.items():
    print(f"\n--- Training {name} ---")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    results[name] = {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }

    print(f"MAE:  {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")
    print(f"R²:   {r2:.3f}")

# Pick Best Model (lowest MAE)
print("\n=== Selecting best model ===")
best_model_name = min(results, key=lambda m: results[m]["MAE"])
best_model = models[best_model_name]

print(f"Best model: {best_model_name}")
print(results[best_model_name])

# Save the best model
joblib.dump(best_model, "delivery_model.joblib")
print("\nModel saved as delivery_model.joblib")

# Also save metrics
pd.DataFrame(results).T.to_json("model_metrics.json", indent=4)
print("Saved model_metrics.json")