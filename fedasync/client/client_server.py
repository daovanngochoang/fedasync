from abc import ABC, abstractmethod
from time import sleep

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from fedasync.commons import QueueConfig, RoutingRules
from fedasync.commons.utils import *
import uuid


class ClientConfig:
    cli_id = None


class ClientServer(ABC):

    def __init__(self, n_epochs: int, queue_connection: BlockingConnection) -> None:
        self.connection: BlockingConnection = queue_connection

        # never change
        self.id = None

        self.id: str = str(uuid.uuid4()) if ClientConfig.cli_id is None else ClientConfig.cli_id
        self.prefix = str(uuid.uuid4())

        self.model = None

        self.client_epoch: int = 0
        self.channel: BlockingChannel = self.connection.channel()
        self.n_epochs: int = n_epochs
        self.acc: float = 0.0
        self.loss: float = 0.0
        self.start: str = ""
        self.end: str = ""
        self.awss3 = AwsS3()

        # self.path_to_weights = self.awss3.tmp + self.weight_file

    def path_to_weights(self):
        weight_file = self.get_weights_file()
        path_to_weights = self.awss3.tmp + weight_file
        return path_to_weights

    def get_weights_file(self):
        weight_file: str = "{}_{}_{}.weights.npy".format(self.prefix, self.id, self.client_epoch)
        return weight_file

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
                if self.n_epochs - self.client_epoch == 0:
                    self.channel.close()
                    self.connection.close()
                    # self.awss3.delete_awss3_file(self.weight_file)
                    break

                # if client epoch is smaller than global epoch => train
                if self.client_epoch < global_msg.current_epoch and self.id in global_msg.chosen_id:
                    print("start local training")
                    print("local epoch: ", self.client_epoch)
                    print("server epoch: ", global_msg.current_epoch)
                    self.start = time_now()
                    self.client_epoch = global_msg.current_epoch
                    self.create_model()

                    self.awss3.download_awss3_file(global_msg.weight_file)

                    weights = load_array(self.awss3.tmp + global_msg.weight_file)

                    self.set_weights(weights)

                    print(self.model.summary())

                    self.data_preprocessing()

                    print("Fit")
                    # train
                    self.fit()

                    # eval
                    print("Evaluate")
                    self.evaluate()

                    sleep(5)

                    self.get_weights()

                    # upload to aws s3 first.
                    self.awss3.upload_file_to_awss3(self.get_weights_file())

                    # get the end time
                    self.end = time_now()

                    # Generate update msg
                    update_msg = UpdateMessage(
                        client_id=self.id, epoch=self.client_epoch,
                        weight_file=self.get_weights_file(),
                        acc=self.acc, loss=self.loss, start=self.start
                    )

                    # Encode and send
                    encoded_update_msg = encode_update_msg(update_msg)

                    print("Send to server")
                    self.send_to_server(RoutingRules.LOCAL_UPDATE, encoded_update_msg)

                    # reset data
                    self.start = ""
                    self.end = ""

    def send_to_server(self, routing_key: str, body):
        """Send msg to server
        """
        self.channel.basic_publish(
            exchange=QueueConfig.EXCHANGE,
            routing_key=routing_key,
            body=body)

    @abstractmethod
    def set_weights(self, weights):
        pass

    @abstractmethod
    def get_weights(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def data_preprocessing(self):
        """

        Returns
        -------

        """

    @abstractmethod
    def create_model(self):
        """
        """
