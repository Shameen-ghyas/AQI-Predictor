import numpy as np
def create_sequences(X, y, sequence_length=7):
    """
    Create sequences of data for time series prediction.

    Parameters:
    X (pd.DataFrame): Feature data.
    y (pd.DataFrame): Target data.
    sequence_length (int): Length of the sequences to create.

    Returns:
    tuple: A tuple containing the sequences of features and targets.
    """
    X_seq = []
    y_seq = []

    for i in range(len(X) - sequence_length):
        X_seq.append(X.iloc[i:i + sequence_length].values)
        y_seq.append(y.iloc[i + sequence_length].values)

    return np.array(X_seq), np.array(y_seq)