# Merge AQI and weather data
import pandas as pd

def merge_data(aq_data, weather_data):
    df_aq = pd.DataFrame(aq_data["hourly"])
    df_weather = pd.DataFrame(weather_data["hourly"])
    df = df_aq.merge(df_weather, on="time")
    df = df.fillna(method="ffill")  # simple fill for missing values
    return df

def handle_lag_nulls(df):
    """
    Clean NaNs created by lag/rolling features.
    For AQI forecasting, it's usually best to drop those first few rows.
    """
    lag_cols = [col for col in df.columns if "lag" in col or "rolling" in col]
    df = df.dropna(subset=lag_cols)
    return df