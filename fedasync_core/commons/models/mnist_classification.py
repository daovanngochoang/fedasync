import tensorflow as tf
from tensorflow.keras import layers, models

mnist_classification = models.Sequential()
mnist_classification.add(layers.Flatten(input_shape=(28, 28)))
mnist_classification.add(layers.Dense(128, activation='relu'))
mnist_classification.add(layers.Dense(10, activation='softmax'))
mnist_classification.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
