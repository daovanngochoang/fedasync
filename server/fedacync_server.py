from commons.config import *
from commons.objects.client import Client
from commons.utils.time_helpers import time_now
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
from client_manager import ClientManager
import sys, os
from commons.utils.message_helper import *
from commons.utils.weight_file_helpers import *


class Server:

    def __init__(self, strategy: Strategy, queue_connection: BlockingConnection) -> None:

        self.strategy: Strategy = strategy
        self.connection: BlockingConnection = queue_connection

        self.channel: BlockingChannel = self.connection.channel()
        self.client_manager: ClientManager = ClientManager()

    def get_msg(self):
        method_frame, header_frame, body = self.channel.basic_get(QueueConfig.SERVER_QUEUE)
        self.channel.basic_ack(method_frame.delivery_tag)
        return method_frame, header_frame, body

    def start(self):

        try:
            while True:
                # connect to queue server and create queue
                self.setup()

                method_frame: Basic.GetOk
                header_frame: BasicProperties
                method_frame, header_frame, body = self.get_msg()

                # Listen to server queue and get all register message
                while method_frame:
                    routing_key = method_frame.routing_key
                    if routing_key == RoutingRules.CLIENTS_REGISTER:
                        new_client = Client(id=body.decode())
                        self.client_manager.add_client(new_client)

                        method_frame, header_frame, body = self.get_msg()

                # get all available
                n_available = self.client_manager.total()

                # if enough clients => start training
                if self.strategy.start_condition(n_available):
                    self.fit()
                    break

        except KeyboardInterrupt:
            print('Interrupted')
            try:
                self.stop()
                sys.exit(0)
            except SystemExit:
                os._exit(0)

    def fit(self):
        """
        Start training distributed on multiple workers
        """
        # start new epoch
        self.new_epoch([])

        while True:

            """----------------------Handle Update message---------------------------"""
            method_frame: Basic.GetOk
            header_frame: BasicProperties

            # Get msg and redirect
            method_frame, header_frame, body = self.get_msg()

            if method_frame:
                routing_key = method_frame.routing_key

                # update prams routing key
                if routing_key == RoutingRules.LOCAL_UPDATE:
                    # decode msg to rabbitmq msg
                    decoded_msg = decode_update_msg(body)

                    # get the weight and bias from s3
                    download_awss3_file(file_name=decoded_msg.weight_file)
                    download_awss3_file(file_name=decoded_msg.bias_file)

                    if (self.strategy.first_finished and self.strategy.latest_finished) is None:
                        self.strategy.first_finished = self.strategy.latest_finished = time_now()
                    elif self.strategy.first_finished is not None:
                        self.

                    # update client stage
                    self.client_manager.update_local_params(decoded_msg)

            """------------------------Checking for update-------------------------------"""
            # Check the update condition asynchronously
            finished_clients = self.client_manager.filter_finished_clients_by_epoch(self.strategy.current_epoch)

            # if the update condition is true
            if self.strategy.check_update(len(finished_clients)):

                # Update
                self.strategy.aggregate(finished_clients)

                # Save value to history
                self.client_manager.save_history(self.strategy.current_epoch)

                # select clients
                selected_clients = self.strategy.select_client(
                    self.client_manager.client_pools
                )

                # if training process is not finished => new epoch
                if not (self.strategy.is_finish()):
                    self.new_epoch(selected_clients)

                # If training process is done => break
                elif self.strategy.is_finish():
                    self.stop()
                    break

    def new_epoch(self, selected_clients):
        # Generate new params
        global_weight_file, global_bias_file = self.strategy.initialize_parameters()

        # select clients
        chosen_id = self.strategy.select_client(selected_clients)

        # create msg object
        msg = GlobalMessage(chosen_id=chosen_id, current_epoch=self.strategy.current_epoch,
                            n_epochs=self.strategy.n_epochs,
                            weight_file=global_weight_file, bias_file=global_bias_file)

        # encode
        str_msg = encode_global_msg(msg)

        # Delete old msg in the queue
        self.channel.queue_purge(QueueConfig.CLIENT_QUEUE)

        # Send new generated params
        self.send_to_clients(RoutingRules.NEW_EPOCH, str_msg)

    def stop(self):
        """Stop training and release resource
        """
        self.channel.close()
        self.connection.close()

    def setup(self) -> None:
        """Connect to queue server and create queue, setup binding key, exchange for queue
        """
        # create server and client queue.
        self.channel.queue_declare(QueueConfig.SERVER_QUEUE, durable=True)
        self.channel.queue_declare(QueueConfig.CLIENT_QUEUE, durable=True)

        # create exchange
        self.channel.exchange_declare(QueueConfig.EXCHANGE, exchange="direct")

        # binding server queue to the related reouting key in queue config.
        self.channel.queue_bind(
            queue=QueueConfig.SERVER_QUEUE,
            exchange=QueueConfig.EXCHANGE,
            routing_key=RoutingRules.LOCAL_UPDATE)

        self.channel.queue_bind(
            queue=QueueConfig.SERVER_QUEUE,
            exchange=QueueConfig.EXCHANGE,
            routing_key=RoutingRules.CLIENTS_REGISTER)

        # binding client queue to it's routing key in queue config
        self.channel.queue_bind(
            queue=QueueConfig.CLIENT_QUEUE,
            exchange=QueueConfig.EXCHANGE,
            routing_key=RoutingRules.NEW_EPOCH)

    def send_to_clients(self, routing_key: str, body) -> None:
        """Send message with routing key
        """
        self.channel.basic_publish(
            exchange=QueueConfig.EXCHANGE,
            routing_key=routing_key,
            body=body)
