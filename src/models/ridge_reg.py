from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor

def get_model():
    return MultiOutputRegressor(
        Ridge(alpha=1.0)
    )