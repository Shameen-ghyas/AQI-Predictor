# Orchestrates the pipeline
from datetime import datetime, timedelta
import pandas as pd
from config import LAT, LON, DATA_DIR
from fetch_data import safe_api_call
from preprocess import merge_data, handle_lag_nulls
from features import build_features
from hopsworks_utils import upload_to_hopsworks, load_from_hopsworks

if __name__ == "__main__":
    start_date = (datetime.today() - timedelta(days=1461)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")

    # Try API
    aq_data = safe_api_call("https://air-quality-api.open-meteo.com/v1/air-quality",
                            {"latitude": LAT, "longitude": LON, "hourly": ( "pm10,"
    "pm2_5,"
    "carbon_monoxide,"
    "nitrogen_dioxide,"
    "sulphur_dioxide,"
    "ozone,"
    "us_aqi"),
                             "start_date": start_date, "end_date": end_date, "timezone": "auto"})
    weather_data = safe_api_call("https://archive-api.open-meteo.com/v1/archive",
                                 {"latitude": LAT, "longitude": LON, "hourly": (    "temperature_2m,"
    "relative_humidity_2m,"
    "dew_point_2m,"
    "precipitation,"
    "surface_pressure,"
    "cloud_cover,"
    "wind_speed_10m,"
    "wind_direction_10m"
),
                                  "start_date": start_date, "end_date": end_date, "timezone": "auto"})

    if aq_data and weather_data:
        df_raw = merge_data(aq_data, weather_data)
        

    else:
        print("API failed. Loading stored data...")
        df_raw = load_from_hopsworks()  # Load from Hopsworks if API fails
        print("Loaded data from Hopsworks.")

    df_features = build_features(df_raw)
    df_features = handle_lag_nulls(df_features)   # organized null handling
   
    df_features["aqi_day1"] = df_features["us_aqi"].shift(-1)
    df_features["aqi_day2"] = df_features["us_aqi"].shift(-2)
    df_features["aqi_day3"] = df_features["us_aqi"].shift(-3)
 
    df_features = df_features.dropna()
    df_features.to_csv(f"{DATA_DIR}/raw_data.csv", index=False)

    upload_to_hopsworks(df_features)

    print("Pipeline finished successfully.")
