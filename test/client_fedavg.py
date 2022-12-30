from pika import BlockingConnection
import tensorflow as tf
from tensorflow.keras import layers, models, datasets
import pika
from client.client_server import ClientServer

rabbitmq_connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/%2F"))

# Get data
(train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
# Normalize pixel values to be between 0 and 1
train_images, test_images = train_images / 255.0, test_images / 255.0

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

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])


class ClientTensorflow(ClientServer):

    def __init__(self, tf_model, queue_connection: BlockingConnection):
        super().__init__(queue_connection)

        self.model = tf_model

    def get_params(self) -> None:
        # get weight and bias of the model
        weight, bias = self.model.get_weights()
        self.save_weight_bias(weight, bias)

    def fit(self):
        pass

    def evaluate(self):
        pass
