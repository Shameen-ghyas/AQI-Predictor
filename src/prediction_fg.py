import joblib
import hopsworks
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import load_model

from config import API_KEY

# Connect to Hopsworks

project = hopsworks.login(api_key_value=API_KEY)
fs = project.get_feature_store()

# SOURCE FEATURE GROUP
# Read historical AQI features from this Feature Group

SOURCE_FG_NAME = "aqi_daily_features"
SOURCE_FG_VERSION = 5

source_fg = fs.get_feature_group(
    name=SOURCE_FG_NAME,
    version=SOURCE_FG_VERSION
)

print(f"Reading data from Feature Group: {SOURCE_FG_NAME} (v{SOURCE_FG_VERSION})")

df = source_fg.read()

# Data preprocessing

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

target_cols = ["aqi_day1", "aqi_day2", "aqi_day3"]

X = df.drop(columns=["time"] + target_cols)
X = X.select_dtypes(include=["number"])

# Load scaler
scaler = joblib.load("saved_models/scaler.pkl")
X_scaled = scaler.transform(X)

sequence_length = 24

latest_sequence = X_scaled[-sequence_length:]
latest_sequence = latest_sequence.reshape(
    1,
    sequence_length,
    latest_sequence.shape[1]
)
# Load trained model

model = load_model(
    "saved_models/gru_model.h5",
    compile=False
)

prediction = model.predict(latest_sequence)

aqi_day1 = float(prediction[0][0])
aqi_day2 = float(prediction[0][1])
aqi_day3 = float(prediction[0][2])

print("\nPredictions")
print("--------------------")
print(f"Day 1 AQI : {aqi_day1:.2f}")
print(f"Day 2 AQI : {aqi_day2:.2f}")
print(f"Day 3 AQI : {aqi_day3:.2f}")

# DESTINATION FEATURE GROUP
# Store predictions here

DEST_FG_NAME = "aqi_predictions"
DEST_FG_VERSION = 1

prediction_fg = fs.get_feature_group(
    name=DEST_FG_NAME,
    version=DEST_FG_VERSION
)

print(f"Writing predictions to Feature Group: {DEST_FG_NAME} (v{DEST_FG_VERSION})")

prediction_df = pd.DataFrame({
    "prediction_time": [datetime.now()],
    "aqi_day1": [aqi_day1],
    "aqi_day2": [aqi_day2],
    "aqi_day3": [aqi_day3],
    "model_name": ["GRU"],
    "model_version": [1]
})

prediction_fg.insert(prediction_df)

print("Prediction uploaded successfully!")