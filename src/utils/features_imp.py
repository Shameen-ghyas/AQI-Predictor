import pandas as pd

def show_feature_importance(model, feature_names, top_n=10):
    importance = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="Importance",
        ascending=False
    )                                                       

    print("\nTop Feature Importances")
    print(importance.head(top_n))