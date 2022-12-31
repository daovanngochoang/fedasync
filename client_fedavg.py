from typing import Dict

import numpy as np
from keras_preprocessing.image import ImageDataGenerator
from pika import BlockingConnection
from keras import datasets
import pika

from fedasync_core.client.client_server import ClientServer
from fedasync_core.commons.config import Config
from fedasync_core.commons.models.cifar10_classification_mode import cifar10_classification
from fedasync_core.commons.utils.numpy_file_helpers import save_array

rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(
    "amqp://guest:guest@localhost:5672/%2F")
)

# Assign config for server.
Config.TMP_FOLDER = "./tmp/client_tmp/"
Config.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
Config.AWS_SECRET_ACCESS_KEY = "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"
Config.BUCKET_NAME = "fedasync"


class ClientTensorflow(ClientServer):

    def __init__(self, n_epochs, queue_connection: BlockingConnection):
        super().__init__(n_epochs, queue_connection)

        self.data: Dict[int, Data] = {}

    def data_preprocessing(self):
        (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
        # Normalize pixel values to be between 0 and 1
        train_images, test_images = train_images / 255.0, test_images / 255.0

        for i in range(self.n_epochs):
            self.data[i] = Data(
                X_train=train_images[int(len(train_images) / 10) * i:int(len(train_images) / 10) * (i + 1)],
                y_train=train_labels[int(len(train_labels) / 10) * i:int(len(train_labels) / 10) * (i + 1)],
                X_test=test_images[int(len(test_images) / 10) * i:int(len(test_images) / 10) * (i + 1)],
                y_test=test_labels[int(len(test_labels) / 10) * i:int(len(test_labels) / 10) * (i + 1)]
            )

    def create_model(self):
        self.model = cifar10_classification

    def get_weights(self) -> None:
        # get weight and bias of the model
        weights = self.model.get_weights()
        save_array(np.array(weights, dtype=object), self.path_to_weights)

    def set_weights(self, weights):
        self.model.set_weights(weights)

    def fit(self):
        data: Data = self.data[self.client_epoch]
        # Image Data Generator , we are shifting image across width and height
        # also we are flipping the image horizontally.
        datagen = ImageDataGenerator(width_shift_range=0.1, height_shift_range=0.1, horizontal_flip=True,
                                     rotation_range=20)
        it_train = datagen.flow(data.X_train, data.y_train)
        self.model.fit(it_train, epochs=10)

    def evaluate(self):
        data: Data = self.data[self.client_epoch]
        # Image Data Generator , we are shifting image accross width and height
        # also we are flipping the image horizantally.
        datagen = ImageDataGenerator(width_shift_range=0.1, height_shift_range=0.1, horizontal_flip=True,
                                     rotation_range=20)
        it_eval = datagen.flow(data.X_test, data.y_test)
        self.loss, self.acc = self.model.evaluate(it_eval, epochs=10)


class Data:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test


client = ClientTensorflow(10, rabbitmq_connection)

client.start_listen()
