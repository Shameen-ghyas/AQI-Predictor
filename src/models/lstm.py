from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout 

def get_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=False),

        Dense(32, activation='relu'),  # another hidden layer with 16 units and ReLU activation
        Dense(3)  # output layer with 3 units for regression (no activation function)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model