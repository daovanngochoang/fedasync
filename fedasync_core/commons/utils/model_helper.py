import numpy as np
from tensorflow.keras.utils import to_categorical


def reshape(np_array):
    if len(np_array.shape) < 4:
        X_list = []
        for char in np_array:
            new_dim = np.expand_dims(char, axis=2)
            X_list.append(new_dim)
        X_reshape = np.array(X_list)
        return X_reshape

def to_index(char):
    CHAR = '0123456789abcdefghklmnpstuvxyz'
    return CHAR.find(char)

def label_encoding(y):
    y_list = []
    for label in y:
        index = to_index(label)
        y_list.append(index)
    encoded = to_categorical(y_list)
    return encoded
