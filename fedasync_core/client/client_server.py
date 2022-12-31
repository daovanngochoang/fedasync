from abc import ABC, abstractmethod

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from fedasync_core.commons.utils.time_helpers import time_now
from fedasync_core.commons.config import QueueConfig, RoutingRules
from fedasync_core.commons.utils.message_helper import *
from fedasync_core.commons.utils.weight_file_helpers import upload_file_to_awss3, save_nparray_to_file
import uuid


class ClientServer(ABC):

    def __init__(self, n_epochs: int, queue_connection: BlockingConnection) -> None:
        self.connection: BlockingConnection = queue_connection

        # never change
        self.id: str = str(uuid.uuid4())
        self.prefix = str(uuid.uuid4())

        self.weight_file: str = "{}_{}.weight".format(self.prefix, self.id)
        self.bias_file = "{}_{}.bias".format(self.prefix, self.id)

        self.client_epoch: int = 0
        self.channel: BlockingChannel = self.connection.channel()
        self.n_epochs: int = n_epochs
        self.acc: float = 0.0
        self.loss: float = 0.0
        self.start: str = ""
        self.end: str = ""

    def start_listen(self) -> None:
        """Listen to training events
        """

        # send register
        self.send_to_server(RoutingRules.CLIENTS_REGISTER, self.id)

        while True:
            method_frame: Basic.GetOk
            header_frame: BasicProperties
            method_frame, header_frame, body = self.channel.basic_get(QueueConfig.CLIENT_QUEUE)

            # close channel to avoid blocking then reconnect
            self.channel.close()
            self.channel = self.connection.channel()

            if method_frame:

                # decode
                global_msg: GlobalMessage = decode_global_msg(body)

                # if the all epochs complete => release and break
                if global_msg.n_epochs - global_msg.current_epoch == 0:
                    self.channel.close()
                    self.connection.close()
                    break

                # if client epoch is smaller than global epoch => train
                if self.client_epoch < global_msg.current_epoch:
                    self.start = time_now()

                    # train
                    self.fit()

                    # eval
                    self.evaluate()

                    # upload to aws s3 first.
                    upload_file_to_awss3(self.weight_file)
                    upload_file_to_awss3(self.bias_file)

                    # get the end time
                    self.end = time_now()

                    # Generate update msg
                    update_msg = UpdateMessage(
                        client_id=self.id, epoch=self.client_epoch,
                        weight_file=self.weight_file, bias_file=self.bias_file,
                        acc=self.acc, loss=self.loss, start=self.start, end=self.end
                    )

                    # Encode and send
                    encoded_update_msg = encode_update_msg(update_msg)

                    self.send_to_server(RoutingRules.LOCAL_UPDATE, encoded_update_msg)

                    # reset data
                    self.client_epoch += 1
                    self.start = ""
                    self.end = ""

    def send_to_server(self, routing_key: str, body):
        """Send msg to server
        """
        self.channel.basic_publish(
            exchange=QueueConfig.EXCHANGE,
            routing_key=routing_key,
            body=body)

    def save_weight_bias(self, weight, bias):
        # save to file
        save_nparray_to_file(weight, self.weight_file)
        save_nparray_to_file(bias, self.bias_file)

    @abstractmethod
    def get_params(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass
