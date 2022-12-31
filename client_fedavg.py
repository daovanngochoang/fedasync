
import numpy as np
from pika import BlockingConnection
import pika

from fedasync_core.client.client_server import ClientServer
from fedasync_core.commons.config import Config
from fedasync_core.commons.models.lenet import LeNet
from fedasync_core.commons.utils.numpy_file_helpers import save_array
from fedasync_core.commons.utils.model_helper import *

import pickle
import os


rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(
    "amqp://guest:guest@localhost:5672/%2F")
)

# Assign config for server.
Config.TMP_FOLDER = "./tmp/client_tmp/"
Config.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
Config.AWS_SECRET_ACCESS_KEY = "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"
Config.BUCKET_NAME = "fedasync"



class ClientTensorflow(ClientServer):
    def __init__(self, n_epochs, queue_connection: BlockingConnection, num_dataset: int):
        super().__init__(n_epochs, queue_connection)
        self.create_model()
        self.data_processing(num_dataset)


    # load data from data folder 
    # then preprocess it to fit the training format of dataset
    def data_preprocessing(self, num_dataset):
        # load data from pickle file
        # X_train, x_test is in the dim (size, 48, 48)
        # y_train, y_test is in the dim (size, )
        # the value is not in the encoding format 
        # --> transfer using to_categorical function
        file = "data{}char48_chunk{}.pkl".format(os.sep, num_dataset)
        with open(file, 'rb') as f:
            x_train, x_test, y_train, y_test = pickle.load(f)
        # processing to the right format
            # reshape X
        self.x_train = reshape(x_train)
        self.x_test = reshape(x_test)
        # label encoding Y
        self.y_train = label_encoding(y_train)
        self.y_test = label_encoding(y_test)
            
            
    def create_model(self):
        self.model = LeNet()
        
    def set_weights(self, weights):
        self.model.set_weights(weights)

    def get_weights(self):
        # get weight and bias of the model
        weights = self.model.get_weights()
        save_array(np.array(weights, dtype=object), self.path_to_weights)

    # sending the result to the master each epoch
    def fit(self):
        self.model.fit(self.x_train, self.y_train, batch_size=64)

    def evaluate(self):
        self.loss, self.acc = self.model.evaluate(self.x_test, self.y_test)


import random

rand = random.randrange(1, 10)
client = ClientTensorflow(10, rabbitmq_connection, num_dataset = rand)

client.start_listen()
