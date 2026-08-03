import os

import pandas as pd
from models.gru import get_model
from utils.sequence import create_sequences
from utils.metrics import evaluate
from config import DATA_DIR
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
from utils.plots import (
    plot_actual_vs_predicted,
    plot_loss
)
from utils.results_logger import save_results
import joblib
import os

df = pd.read_csv(DATA_DIR / "raw_data.csv")

# Define the features and target

target_cols = ["aqi_day1", "aqi_day2", "aqi_day3"]

train_size = int(len(df) * 0.8)

train = df.iloc[:train_size]
test = df.iloc[train_size:]

X_train = train.drop(columns=["time"] + target_cols).select_dtypes(include=["number"])
X_test = test.drop(columns=["time"] + target_cols).select_dtypes(include=["number"])

y_train = train[target_cols]
y_test = test[target_cols]

# Scale the features using MinMaxScaler

scaler = MinMaxScaler()

X_train = pd.DataFrame(
    scaler.fit_transform(X_train),
    columns=X_train.columns
)

X_test = pd.DataFrame(
    scaler.transform(X_test),
    columns=X_test.columns
)
# Create sequences

sequence_length = 24

X_train_seq, y_train_seq = create_sequences(
    X_train,
    y_train,
    sequence_length
)

X_test_seq, y_test_seq = create_sequences(
    X_test,
    y_test,
    sequence_length
)

# save the scaler for future use

os.makedirs("saved_models", exist_ok=True)

joblib.dump(
    scaler,
    "saved_models/scaler.pkl"
)

print("Scaler saved!")

# create and compile the GRU model

model = get_model(
    input_shape=(X_train_seq.shape[1], X_train_seq.shape[2])
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

# Train the model
print("Training GRU...")
history = model.fit(
    X_train_seq,
    y_train_seq,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    verbose=1,
    callbacks=[early_stop]
)

# predict on the test set

y_pred_seq = model.predict(X_test_seq)

# plotting the results

plot_loss(
    history,
    "GRU"
)

plot_actual_vs_predicted(
    y_test_seq,
    y_pred_seq,
    "GRU"
)

# Evaluate the model

overall_metrics, target_metrics = evaluate(
    y_test_seq,
    y_pred_seq,
    target_cols
)

# log the results

save_results(
    "GRU",
    overall_metrics
)

# Print the evaluation metrics  
for metric, value in overall_metrics.items():
    print(f"{metric}: {value:.4f}")

for target, metrics in target_metrics.items():
    print(f"\n{target}")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")

# Save the trained model
model.save("saved_models/gru_model.h5")