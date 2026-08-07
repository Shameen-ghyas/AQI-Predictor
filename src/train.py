import hopsworks
from config import API_KEY 
import pandas as pd
from models.random_forest import get_model as rf_model
from models.ridge_reg import get_model as ridge_model
from utils.metrics import evaluate
from utils.registry import upload_model, save_model
from utils.features_imp import show_feature_importance
from utils.plots import (
    plot_actual_vs_predicted,
    plot_residuals,
    plot_feature_importance
)
from utils.results_logger import save_results


# Connect to Hopsworks and load the feature group
project = hopsworks.login(api_key_value=API_KEY)
fs = project.get_feature_store()
fg = fs.get_feature_group(name="aqi_daily_features", version=5)
df = fg.read()

# Prepare the data for training
target_cols = ["aqi_day1", "aqi_day2", "aqi_day3"]

train_size = int(len(df) * 0.8)
train = df.iloc[:train_size]
test = df.iloc[train_size:]

X_train = train.drop(columns=["time"] + target_cols).select_dtypes(include=["number"])

X_test = test.drop(columns=["time"] + target_cols).select_dtypes(include=["number"])

y_train = train[target_cols]

y_test = test[target_cols]

# Train the model
models = {
    "RandomForest": rf_model(),
    "Ridge": ridge_model(),
}

# Train each model
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    overall_metrics, target_metrics = evaluate(
        y_test,
        y_pred,
        target_cols
    )

    # Generate plots
    plot_actual_vs_predicted(
        y_test.values,
        y_pred,
        name
    )

    plot_residuals(
        y_test.values,
        y_pred,
        name
    )

    print("\nOverall Performance")

    for metric, value in overall_metrics.items():
        print(f"{metric}: {value:.4f}")

    print("\nPer Target Performance")

    for target, metrics in target_metrics.items():
        print(f"\n{target}")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")

    # Feature importance (only if supported)
    if hasattr(model, "feature_importances_"):
        show_feature_importance(model, X_train.columns)

        plot_feature_importance(
            model,
            X_train.columns,
            name
        )

    model_slug = name.lower().replace(" ", "_")
    model_file_path = f"saved_models/{model_slug}.pkl"
    save_results(f"model_{model_slug}", overall_metrics)

    # Save the trained model
    save_model(
        model,
        model_file_path
    )

    # Upload the model to Hopsworks
    try:
        upload_model(
            project=project,
            model_name=f"aqi_predictor_{model_slug}",
            model_file_path=model_file_path,
            version=2,
            metrics=overall_metrics,
            description=f"{name} multi-output AQI predictor"
        )
    except Exception as e:
        print("\nModel upload failed.")
        print(e)