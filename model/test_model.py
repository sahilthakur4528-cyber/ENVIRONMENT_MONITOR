from predict import predict_aqi

aqi = predict_aqi(
    75,
    120,
    1.2,
    40,
    20,
    35,
    30,
    60
)

print("Predicted AQI:", aqi)