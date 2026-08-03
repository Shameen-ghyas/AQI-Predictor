from dotenv import load_dotenv
import hopsworks
import os
import pandas as pd

load_dotenv()

project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY")) 
fs = project.get_feature_store()

df = pd.read_csv("data/raw/raw_data.csv")

fg = fs.get_or_create_feature_group(
    name="aqi_features",
    version=1,
    primary_key=["time"],
    description="Karachi AQI and weather features",
    time_travel_format="HUDI"
)

fg.insert(df)