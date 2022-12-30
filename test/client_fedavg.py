from typing import Dict

from pika import BlockingConnection
import tensorflow as tf
from keras import layers, models, datasets
import pika
from client.client_server import ClientServer

rabbitmq_connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/%2F"))


class Data:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

class ClientTensorflow(ClientServer):

    def __init__(self, n_epochs, queue_connection: BlockingConnection):
        super().__init__(n_epochs, queue_connection)

        self.model = None
        self.data: Dict[str, Data]

    def data_preprocessing(self):
        (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
        # Normalize pixel values to be between 0 and 1
        train_images, test_images = train_images / 255.0, test_images / 255.0

        for i in range(self.n_epochs):
            self.data[i] = Data

    def create_model(self):
        self.model = models.Sequential()
        self.model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(64, activation='relu'))
        self.model.add(layers.Dense(10))

        self.model.compile(optimizer='adam',
                           loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                           metrics=['accuracy'])

    def get_params(self) -> None:
        # get weight and bias of the model
        weight, bias = self.model.get_weights()
        self.save_weight_bias(weight, bias)

    def fit(self):
        self.model.fit(train_images, train_labels, epochs=1, validation_data=(test_images, test_labels))
        pass

    def evaluate(self):
        pass
