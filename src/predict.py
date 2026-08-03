import joblib
import hopsworks
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import load_model

from config import API_KEY

# Connect to Hopsworks

project = hopsworks.login(api_key_value=API_KEY)
fs = project.get_feature_store()

# Read latest data

fg = fs.get_feature_group(
    name="aqi_daily_features",
    version=4
)

df = fg.read()

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

# Prepare latest sequence

target_cols = ["aqi_day1", "aqi_day2", "aqi_day3"]

X = df.drop(columns=["time"] + target_cols)

X = X.select_dtypes(include=["number"])

# Download scaler from Hopsworks Model Registry

mr = project.get_model_registry()

scaler_model = mr.get_model(
    name="aqi_scaler",
    version=1
)

scaler_dir = scaler_model.download()

scaler = joblib.load(
    f"{scaler_dir}/scaler.pkl"
)

X_scaled = scaler.transform(X)

sequence_length = 24

latest_sequence = X_scaled[-sequence_length:]

latest_sequence = latest_sequence.reshape(
    1,
    sequence_length,
    latest_sequence.shape[1]
)

# Download GRU model from Hopsworks Model Registry

gru_model = mr.get_model(
    name="aqi_predictor_gru",
    version=1
)

gru_dir = gru_model.download()

model = load_model(
    f"{gru_dir}/gru_model.h5",
    compile=False
)

# Predict

prediction = model.predict(latest_sequence)

aqi_day1 = float(prediction[0][0])
aqi_day2 = float(prediction[0][1])
aqi_day3 = float(prediction[0][2])

print("\nPredictions")
print("--------------------")
print(f"Day 1 AQI : {aqi_day1:.2f}")
print(f"Day 2 AQI : {aqi_day2:.2f}")
print(f"Day 3 AQI : {aqi_day3:.2f}")


# Upload prediction

prediction_fg = fs.get_feature_group(
    name="aqi_predictions",
    version=1
)

prediction_df = pd.DataFrame({
    "prediction_time": [datetime.now()],
    "aqi_day1": [aqi_day1],
    "aqi_day2": [aqi_day2],
    "aqi_day3": [aqi_day3],
    "model_name": ["GRU"],
    "model_version": [1]
})

prediction_fg.insert(prediction_df)

print("\nPrediction uploaded successfully!")