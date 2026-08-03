import os
import pandas as pd

RESULTS_FILE = "results/model_results.csv"


def save_results(model_name, overall_metrics):

    os.makedirs("results", exist_ok=True)

    row = {
        "Model": model_name,
        "MSE": overall_metrics["MSE"],
        "RMSE": overall_metrics["RMSE"],
        "MAE": overall_metrics["MAE"],
        "R2": overall_metrics["R2"]
    }

    # Create file if it doesn't exist
    if not os.path.exists(RESULTS_FILE):
        df = pd.DataFrame(columns=row.keys())
    else:
        df = pd.read_csv(RESULTS_FILE)

    # Update if model already exists
    if model_name in df["Model"].values:
        df.loc[df["Model"] == model_name] = row
    else:
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv(RESULTS_FILE, index=False)

    print(f"{model_name} results saved to {RESULTS_FILE}")