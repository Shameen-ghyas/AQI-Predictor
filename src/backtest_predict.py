# import argparse
# from pathlib import Path

# import joblib
# import numpy as np
# import pandas as pd
# from tensorflow.keras.models import load_model


# TARGET_COLS = ["aqi_day1", "aqi_day2", "aqi_day3"]


# def parse_args():
#     parser = argparse.ArgumentParser(
#         description="Standalone backtest for 3-step AQI prediction."
#     )
#     parser.add_argument(
#         "--data",
#         type=Path,
#         default=Path("data/raw/raw_data.csv"),
#         help="Path to dataset with engineered features and target columns.",
#     )
#     parser.add_argument(
#         "--model",
#         type=Path,
#         default=Path("saved_models/gru_model.h5"),
#         help="Path to trained Keras model.",
#     )
#     parser.add_argument(
#         "--scaler",
#         type=Path,
#         default=Path("saved_models/scaler.pkl"),
#         help="Path to fitted feature scaler.",
#     )
#     parser.add_argument(
#         "--sequence-length",
#         type=int,
#         default=24,
#         help="Sequence length used during model training.",
#     )
#     parser.add_argument(
#         "--holdout-ratio",
#         type=float,
#         default=0.2,
#         help="Fraction of latest rows used for rolling backtest.",
#     )
#     parser.add_argument(
#         "--max-windows",
#         type=int,
#         default=200,
#         help="Maximum rolling cutoffs to evaluate from the holdout region.",
#     )
#     return parser.parse_args()


# def rmse(y_true, y_pred):
#     return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


# def safe_mape(y_true, y_pred):
#     denom = np.where(np.abs(y_true) < 1e-8, 1.0, np.abs(y_true))
#     return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


# def run_backtest(args):
#     if not args.data.exists():
#         raise FileNotFoundError(f"Dataset not found: {args.data}")
#     if not args.model.exists():
#         raise FileNotFoundError(f"Model not found: {args.model}")
#     if not args.scaler.exists():
#         raise FileNotFoundError(f"Scaler not found: {args.scaler}")

#     df = pd.read_csv(args.data)
#     df["time"] = pd.to_datetime(df["time"])
#     df = df.sort_values("time").reset_index(drop=True)

#     missing_targets = [col for col in TARGET_COLS if col not in df.columns]
#     if missing_targets:
#         raise ValueError(f"Missing target columns in dataset: {missing_targets}")

#     feature_frame = df.drop(columns=["time"] + TARGET_COLS).select_dtypes(include=["number"])
#     scaler = joblib.load(args.scaler)
#     model = load_model(args.model, compile=False)
#     scaled_features = scaler.transform(feature_frame)

#     start_idx = max(
#         args.sequence_length - 1,
#         int(len(df) * (1.0 - args.holdout_ratio)),
#     )
#     end_idx = len(df) - 1
#     candidate_indices = list(range(start_idx, end_idx + 1))
#     candidate_indices = candidate_indices[-args.max_windows :]

#     if not candidate_indices:
#         raise ValueError("No valid cutoff windows found. Check sequence length and dataset size.")

#     predictions = []
#     actuals = []
#     times = []

#     for cutoff_idx in candidate_indices:
#         seq_start = cutoff_idx - args.sequence_length + 1
#         sequence = scaled_features[seq_start : cutoff_idx + 1]
#         if len(sequence) != args.sequence_length:
#             continue

#         x_input = sequence.reshape(1, args.sequence_length, sequence.shape[1])
#         y_pred = model.predict(x_input, verbose=0)[0]
#         y_true = df.loc[cutoff_idx, TARGET_COLS].to_numpy(dtype=float)

#         predictions.append(y_pred)
#         actuals.append(y_true)
#         times.append(df.loc[cutoff_idx, "time"])

#     if not predictions:
#         raise ValueError("Backtest produced no predictions.")

#     y_pred_all = np.array(predictions)
#     y_true_all = np.array(actuals)

#     print("\nBacktest summary")
#     print("-" * 50)
#     print(f"Windows tested   : {len(y_pred_all)}")
#     print(f"Cutoff start     : {times[0]}")
#     print(f"Cutoff end       : {times[-1]}")
#     print(f"Model            : {args.model}")
#     print(f"Scaler           : {args.scaler}")

#     for i, target in enumerate(TARGET_COLS):
#         t_true = y_true_all[:, i]
#         t_pred = y_pred_all[:, i]
#         t_mae = float(np.mean(np.abs(t_true - t_pred)))
#         t_rmse = rmse(t_true, t_pred)
#         t_mape = safe_mape(t_true, t_pred)
#         print(f"\n{target}")
#         print(f"  MAE  : {t_mae:.4f}")
#         print(f"  RMSE : {t_rmse:.4f}")
#         print(f"  MAPE : {t_mape:.2f}%")

#     overall_mae = float(np.mean(np.abs(y_true_all - y_pred_all)))
#     overall_rmse = rmse(y_true_all, y_pred_all)
#     overall_mape = safe_mape(y_true_all, y_pred_all)
#     print("\nOverall (all 3 outputs together)")
#     print(f"  MAE  : {overall_mae:.4f}")
#     print(f"  RMSE : {overall_rmse:.4f}")
#     print(f"  MAPE : {overall_mape:.2f}%")

#     preview = pd.DataFrame(
#         {
#             "time": times,
#             "actual_day1": y_true_all[:, 0],
#             "pred_day1": y_pred_all[:, 0],
#             "actual_day2": y_true_all[:, 1],
#             "pred_day2": y_pred_all[:, 1],
#             "actual_day3": y_true_all[:, 2],
#             "pred_day3": y_pred_all[:, 2],
#         }
#     )

#     print("\nSample predictions from the most recent windows")
#     print("-" * 50)
#     print(preview.tail(10).to_string(index=False))


# if __name__ == "__main__":
#     run_backtest(parse_args())

import hopsworks
from config import API_KEY  # or: from config import API_KEY

project = hopsworks.login(api_key_value=API_KEY)
mr = project.get_model_registry()

models_to_upload = [
    {
        "name": "aqi_scaler",
        "version": 1,
        "path": "saved_models/scaler.pkl",  # if your file is named scalar.pkl, change this
        "description": "Feature scaler used for AQI model preprocessing",
    },
]

for m in models_to_upload:
    model_meta = mr.python.create_model(
        name=m["name"],
        version=m["version"],
        description=m["description"],
        metrics={}
    )
    model_meta.save(m["path"])
    print(f"Uploaded {m['name']} v{m['version']} from {m['path']}")