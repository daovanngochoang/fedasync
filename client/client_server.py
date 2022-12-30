from abc import ABC, abstractmethod

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from commons.config import QueueConfig, RoutingRules
from commons.utils.message_helper import *


class ClientServer(ABC):

    def __init__(self, model, queue_connection: BlockingConnection) -> None:
        self.connection: BlockingConnection = queue_connection
        self.model = model

        self.client_epoch: int = 0
        self.channel: BlockingChannel = self.connection.channel()
        self.id: str = ""
        self.param_file: str = ""
        self.acc: float = 0.0
        self.loss: float = 0.0
        self.start: str = ""
        self.end: str = ""

    def start_listen(self) -> None:
        """Listen to training events
        """
        while True:
            method_frame: Basic.GetOk
            header_frame: BasicProperties
            method_frame, header_frame, body = self.channel.basic_get(QueueConfig.CLIENT_QUEUE)

            # close channel to avoid blocking
            self.channel.close()
            self.channel = self.connection.channel()

            if method_frame:
                global_training_info: GlobalMessage = decode_global_msg(body)

                # if client epoch is smaller than global epoch => train
                if self.client_epoch < global_training_info.epoch:
                    # train
                    self.fit()

                    # eval
                    self.evaluate()

                    # Generate update msg
                    update_msg = UpdateMessage(
                        self.id, self.client_epoch, self.param_file, self.acc
                        , self.loss, self.start, self.end
                    )

                    # Encode and send
                    encoded_update_msg = encode_update_msg(update_msg)

                    self.send_update(RoutingRules.LOCAL_UPDATE, encoded_update_msg)

    def send_update(self, routing_key: str, body):
        """Send the update for gradients
        """
        self.channel.basic_publish(
            exchange=QueueConfig.EXCHANGE,
            routing_key=routing_key,
            body=body)

    @abstractmethod
    def get_params(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass
