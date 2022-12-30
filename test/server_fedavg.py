import pika
from server.strategies.fedavg_tensorflow import FedAvgTensorflow
from server.fedacync_server import Server
from keras import layers, models

# connect to queue
rabbitmq_connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/%2F"))


# create tensor flow model
model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(10))

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


