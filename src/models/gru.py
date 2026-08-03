from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense

def get_model(input_shape):
    model = Sequential([
        GRU(64, input_shape=input_shape),
        Dense(32, activation="relu"),
        Dense(3)
    ])

    model.compile(
        optimizer="adam",
        loss="mse",
        metrics=["mae"]
    )

    return model