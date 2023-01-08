import pika

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
fed_avg_tf: FedAvgTensorflow = FedAvgTensorflow(
    model,
    n_epochs=3,
    min_fit_clients=6,
    min_update_clients=4,
    convergent_value=0.1
)

fed_async_server = Server(fed_avg_tf, rabbitmq_connection, time_out=40)

# start listening and waiting for clients to join
fed_async_server.start()
