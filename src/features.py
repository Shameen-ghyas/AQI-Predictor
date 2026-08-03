import pandas as pd
import holidays

# Basic features
def add_time_features(df):
    df["time"] = pd.to_datetime(df["time"])
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["month"] = df["time"].dt.month
    df["day_of_week"] = df["time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    return df

def create_daily_lag_features(df):
    df["aqi_lag_1d"] = df["us_aqi"].shift(1)
    df["aqi_lag_3d"] = df["us_aqi"].shift(3)
    df["aqi_lag_7d"] = df["us_aqi"].shift(7)
    return df

def create_daily_rolling_features(df):
    df["aqi_rolling_7d_avg"] = (
    df["us_aqi"]
      .shift(1)
      .rolling(7)
      .mean()
)
    df["aqi_rolling_14d_avg"] = (
    df["us_aqi"]
      .shift(1)
      .rolling(14)
      .mean()
)
    return df

def add_derived_features(df):
    df["aqi_change_rate"] = (
    df["us_aqi"].shift(1) - df["us_aqi"].shift(2)
)
    return df

# Extra features 
def add_seasonal_features(df):
    df["is_monsoon"] = df["month"].isin([6, 7, 8, 9]).astype(int)
    return df

def add_traffic_features(df):
    df["is_rush_hour"] = df["hour"].isin([7, 8, 9, 17, 18, 19, 20]).astype(int)
    return df

def add_holiday_features(df):
    # Get all unique years in your dataset
    years = df["time"].dt.year.unique()
    
    # Generate Pakistan holidays for those years
    pk_holidays = holidays.PK(years=years)
    
    # Flag rows that fall on a holiday
    df["is_holiday"] = df["time"].dt.date.astype(str).isin([str(d) for d in pk_holidays]).astype(int)
    return df

#  Build all features 
def build_features(df):
    df = add_time_features(df)
    df = create_daily_lag_features(df)
    df = create_daily_rolling_features(df)
    df = add_derived_features(df)
    df = add_seasonal_features(df)
    df = add_traffic_features(df)
    df = add_holiday_features(df)
    df = df.fillna(method="ffill").reset_index(drop=True)
    return df
