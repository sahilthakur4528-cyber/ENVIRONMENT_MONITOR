import joblib

# Load ML Model
model = joblib.load("models/aqi_model.pkl")

# Load Scaler
scaler = joblib.load("models/scaler.pkl")


# ==========================================
# AQI Prediction
# ==========================================

def predict_aqi(pm25,
                pm10,
                co,
                no2,
                so2,
                o3,
                temperature,
                humidity):

    data = [[
        pm25,
        pm10,
        co,
        no2,
        so2,
        o3,
        temperature,
        humidity
    ]]

    data = scaler.transform(data)

    prediction = model.predict(data)

    return round(float(prediction[0]), 2)


# ==========================================
# AQI Category
# ==========================================

def aqi_category(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"