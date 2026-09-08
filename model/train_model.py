# ==========================================
# AQI Prediction Model
# ==========================================

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler

# ==========================================
# Load Dataset
# ==========================================

df = pd.read_csv("dataset/aqi_dataset_1000_records.csv")

# ==========================================
# Features
# ==========================================

X = df[[
    "PM2.5",
    "PM10",
    "CO",
    "NO2",
    "SO2",
    "O3",
    "Temperature",
    "Humidity"
]]

# Target

y = df["AQI"]

# ==========================================
# Scaling
# ==========================================

scaler = StandardScaler()

X = scaler.fit_transform(X)

# ==========================================
# Train Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================
# Model
# ==========================================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ==========================================
# Accuracy
# ==========================================

prediction = model.predict(X_test)

mae = mean_absolute_error(y_test, prediction)

print("Mean Absolute Error :", mae)

# ==========================================
# Save Model
# ==========================================

joblib.dump(model, "models/aqi_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("AQI Model Saved Successfully")