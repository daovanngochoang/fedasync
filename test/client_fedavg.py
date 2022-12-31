from typing import Dict

from pika import BlockingConnection
import tensorflow as tf
from keras import layers, models, datasets
import pika
from client.client_server import ClientServer
from commons.config import ServerConfig
from commons.models.Lenet5 import Lenet5

rabbitmq_connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/%2F"))

# Assign config for server.
ServerConfig.TMP_FOLDER = "./tmp/"
ServerConfig.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
ServerConfig.AWS_SECRET_ACCESS_KEY = "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"
ServerConfig.BUCKET_NAME = "fedasync"

class ClientTensorflow(ClientServer):

    def __init__(self, n_epochs, queue_connection: BlockingConnection):
        super().__init__(n_epochs, queue_connection)

        self.model = None
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
        self.model = Lenet5

    def get_params(self) -> None:
        # get weight and bias of the model
        weight, bias = self.model.get_weights()
        self.save_weight_bias(weight, bias)

    def fit(self):
        data: Data = self.data[self.client_epoch]
        self.model.fit(data.X_train, data.y_train, epochs=10)

    def evaluate(self):
        data: Data = self.data[self.client_epoch]
        self.loss, self.acc = self.model.evaluate(data.X_test, data.y_test, epochs=10)


class Data:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
