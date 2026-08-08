import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate(y_true, y_pred, target_cols):

    overall = {
        "MSE": mean_squared_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAE": mean_absolute_error(y_true, y_pred),
        "R2": r2_score(y_true, y_pred)
    }

    per_target = {}

    for i, target in enumerate(target_cols):
        
        if hasattr(y_true, "iloc"):
            true = y_true.iloc[:, i]
        else:
            true = y_true[:, i]

        pred = y_pred[:, i]

        per_target[target] = {
            "MSE": mean_squared_error(true, pred),
            "RMSE": np.sqrt(mean_squared_error(true, pred)),
            "MAE": mean_absolute_error(true, pred),
            "R2": r2_score(true, pred)
        }

    return overall, per_target