import pika
from tensorflow.keras import datasets

from fedasync.commons import Config
from fedasync.commons.models import mnist_classification
from fedasync.server.strategies import FedAvgTensorflow
from fedasync.server import Server

# connect to queue
rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(
    "amqps://dmtiiogx:1Pf_J9q3HmJ0Fdo9oYu1H2Jbpk4YAKK4@armadillo.rmq.cloudamqp.com/dmtiiogx")
)

# Assign config for server.
Config.TMP_FOLDER = "./tmp/server_tmp/"
Config.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
Config.AWS_SECRET_ACCESS_KEY = "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"
Config.BUCKET_NAME = "fedasync"

# create tensor flow model
model = mnist_classification


# strategy
class FedAvgMnistTensor(FedAvgTensorflow):
    def __init__(self, model, n_epochs: int, min_update_clients: int, min_fit_clients: int, convergent_value: float):
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value)

    def evaluate(self):
        x_test, y_test = self.data_preprocessing()
        loss, acc = self.model.evaluate(x_test, y_test)
        print("loss: {} \nacc: {}\n".format(loss, acc))

    def data_preprocessing(self):
        (x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()

        # Normalize pixel values to be between 0 and 1
        x_train, x_test = x_train / 255.0, x_test / 255.0
        return x_test, y_test


fed_avg_tf = FedAvgMnistTensor(
    model,
    n_epochs=3,
    min_fit_clients=3,
    min_update_clients=2,
    convergent_value=0.1
)
ids_file = "ids"

fed_async_server = Server(fed_avg_tf, rabbitmq_connection, time_out=40)

# start listening and waiting for clients to join
fed_async_server.start()
