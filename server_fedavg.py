import pika

from fedasync_core.commons.config import Config
from fedasync_core.commons.models.cifar10_classification import cifar10_classification
from fedasync_core.commons.models.mnist_classification import mnist_classification
from fedasync_core.server.strategies.fedavg_tensorflow import FedAvgTensorflow
from fedasync_core.server.fedacync_server import Server

# connect to queue
rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(
    "amqp://guest:guest@localhost:5672/%2F")
)

# Assign config for server.
Config.TMP_FOLDER = "./tmp/server_tmp/"
Config.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
Config.AWS_SECRET_ACCESS_KEY = "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"
Config.BUCKET_NAME = "fedasync"


# create tensor flow model
model = mnist_classification

# strategy
fed_avg_tf: FedAvgTensorflow = FedAvgTensorflow(
    model,
    n_epochs=3,
    min_fit_clients=3,
    min_update_clients=2,
    convergent_value=0.1
)

fed_async_server = Server(fed_avg_tf, rabbitmq_connection, time_out=20)

# start listening and waiting for clients to join
fed_async_server.start()
