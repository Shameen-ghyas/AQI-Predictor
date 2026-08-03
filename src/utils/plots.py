from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_DIR = Path("results")


RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _results_path(model_name, suffix):
    slug = model_name.lower().replace(" ", "_")
    return RESULTS_DIR / f"{slug}_{suffix}.png"


def plot_actual_vs_predicted(y_true, y_pred, model_name):

    plt.figure(figsize=(6,6))

    plt.scatter(
        y_true.flatten(),
        y_pred.flatten(),
        alpha=0.5
    )

    mn = min(y_true.min(), y_pred.min())
    mx = max(y_true.max(), y_pred.max())

    plt.plot(
        [mn, mx],
        [mn, mx],
        'r--'
    )

    plt.xlabel("Actual AQI")
    plt.ylabel("Predicted AQI")
    plt.title(f"{model_name} Actual vs Predicted")

    plt.grid(True)

    plt.savefig(_results_path(model_name, "actual"), dpi=300)

    plt.close()



def plot_residuals(y_true, y_pred, model_name):

    residuals = y_true.flatten() - y_pred.flatten()

    plt.figure(figsize=(7,5))

    plt.scatter(
        y_pred.flatten(),
        residuals,
        alpha=0.5
    )

    plt.axhline(
        y=0,
        color="red",
        linestyle="--"
    )

    plt.xlabel("Predicted AQI")
    plt.ylabel("Residual")

    plt.title(f"{model_name} Residual Plot")

    plt.grid(True)

    plt.savefig(_results_path(model_name, "residual"), dpi=300)

    plt.close()



def plot_feature_importance(model, feature_names, model_name):

    importance = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="Importance",
        ascending=False
    ).head(10)

    plt.figure(figsize=(8,5))

    plt.barh(
        importance["Feature"],
        importance["Importance"]
    )

    plt.gca().invert_yaxis()

    plt.title("Top 10 Feature Importances")

    plt.tight_layout()

    plt.savefig(_results_path(model_name, "feature_importance"), dpi=300)

    plt.close()



def plot_loss(history, model_name):

    plt.figure(figsize=(8,5))

    plt.plot(
        history.history["loss"][1:],
        label="Training Loss"
    )

    plt.plot(
        history.history["val_loss"][1:],
        label="Validation Loss"
    )

    plt.xlabel("Epoch")
    plt.ylabel("Loss")

    plt.title(f"{model_name} Loss Curve")

    plt.legend()

    plt.grid(True)

    plt.savefig(_results_path(model_name, "loss"), dpi=300)

    plt.close()