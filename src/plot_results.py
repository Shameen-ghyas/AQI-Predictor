import pandas as pd
import matplotlib.pyplot as plt

# Load results
df = pd.read_csv("results/model_results.csv")

metrics = ["RMSE", "MAE", "R2"]

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, metric in zip(axes, metrics):
    ax.bar(df["Model"], df[metric])
    ax.set_title(metric)
    ax.set_xlabel("Model")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Add values above bars
    for i, value in enumerate(df[metric]):
        ax.text(i, value, f"{value:.3f}",
                ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig("results/model_comparison.png", dpi=300)
plt.show()