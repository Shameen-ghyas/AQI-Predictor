from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout 

def get_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=False),

        Dense(32, activation='relu'), 
        Dense(3) 
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model