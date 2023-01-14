from typing import Dict

import numpy as np
from pika import BlockingConnection
from keras import datasets
import pika

from fedasync.client import ClientServer
from fedasync.client.client_server import ClientConfig
from fedasync.commons import Config
from fedasync.commons.models import *
from fedasync.commons.utils import save_array

rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(
    "amqps://dmtiiogx:1Pf_J9q3HmJ0Fdo9oYu1H2Jbpk4YAKK4@armadillo.rmq.cloudamqp.com/dmtiiogx")
)

# Assign config for server.
Config.TMP_FOLDER = "./tmp/client_tmp/"
Config.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
Config.AWS_SECRET_ACCESS_KEY = "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"
Config.BUCKET_NAME = "fedasync"

ClientConfig.cli_id = "hoangdao.1902093.worker3"

class ClientTensorflow(ClientServer):

    def __init__(self, n_epochs: int = 3, queue_connection: BlockingConnection = None):
        super().__init__(n_epochs, queue_connection)

        self.data = None

    def data_preprocessing(self):
        (x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()

        # Normalize pixel values to be between 0 and 1
        x_train, x_test = x_train / 255.0, x_test / 255.0

        self.data = Data(x_train, y_train, x_test, y_test)

    def create_model(self):
        self.model = mnist_classification

    def get_weights(self) -> None:
        # get weight and bias of the model
        weights = self.model.get_weights()
        save_array(np.array(weights, dtype=object), self.path_to_weights())

    def set_weights(self, weights):
        self.model.set_weights(weights)

    def fit(self):
        self.model.fit(self.data.X_train, self.data.y_train, epochs=1)

    def evaluate(self):
        # Image Data Generator , we are shifting image accross width and height
        # also we are flipping the image horizantally.

        self.loss, self.acc = self.model.evaluate(self.data.X_test, self.data.y_test)
        print("loss: {} \nacc: {}\n".format(self.loss, self.acc))


class Data:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test


client = ClientTensorflow(n_epochs=3, queue_connection=rabbitmq_connection)

client.start_listen()
