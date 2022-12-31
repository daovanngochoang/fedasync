import pika

from commons.config import ServerConfig
from commons.models.cifar10_classification_mode import cifar10_classification
from server.strategies.fedavg_tensorflow import FedAvgTensorflow
from server.fedacync_server import Server

# connect to queue
rabbitmq_connection = pika.BlockingConnection(pika.URLParameters("amqps://dmtiiogx:1Pf_J9q3HmJ0Fdo9oYu1H2Jbpk4YAKK4@armadillo.rmq.cloudamqp.com/dmtiiogx"))

# Assign config for server.
ServerConfig.TMP_FOLDER = "./tmp/"
ServerConfig.AWS_ACCESS_KEY_ID = "AKIARUCJKIXKV24ZV553"
ServerConfig.AWS_SECRET_ACCESS_KEY = "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"
ServerConfig.BUCKET_NAME = "fedasync"

# create tensor flow model
model = cifar10_classification

# strategy
fed_avg_tf: FedAvgTensorflow = FedAvgTensorflow(
    model,
    n_epochs=10,
    min_fit_clients=10,
    min_update_clients=5,
    convergent_value=0.1
)

fed_async_server = Server(fed_avg_tf, rabbitmq_connection)

# start listening and waiting for clients to join
fed_async_server.start()
