import sys
import json
import numpy as np
from tensorflow.keras.models import load_model
import shap

def main():
    model_path = sys.argv[1]
    input_json = sys.stdin.read()
    input_data = json.loads(input_json)

    X = np.array(input_data["X"])
    background = np.array(input_data["background"])

    model = load_model(model_path, compile=False)
    prediction = model.predict(X, verbose=0)

    explainer = shap.GradientExplainer(model, background)
    shap_values = explainer.shap_values(X)

    shap_array = np.array(shap_values)  # (num_outputs, batch, timesteps, features)
    mean_importance = np.mean(np.abs(shap_array), axis=(0, 1, 3)).tolist()

    print(json.dumps({
        "prediction": prediction.tolist(),
        "shap_importance": mean_importance
    }))

if __name__ == "__main__":
    main()