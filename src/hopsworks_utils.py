import hopsworks
from config import API_KEY

def upload_to_hopsworks(df):
    project = hopsworks.login(api_key_value=API_KEY)
    fs = project.get_feature_store()
    fg = fs.get_feature_group(
    name="aqi_daily_features",
    version=5
)

    fg.insert(df)



def load_from_hopsworks(name="aqi_daily_features", version=5):
    project = hopsworks.login(api_key_value=API_KEY)
    fs = project.get_feature_store()
    fg = fs.get_feature_group(name=name, version=version)
    return fg.read()

