from commons.config import *
from commons.objects.client_object import Client
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
from client_manager import ClientManager
import sys, os
from commons.utils.message_helper import *
from commons.aws_s3_manager import *


class Server:

    def __init__(self, strategy: Strategy, queue_connection: BlockingConnection) -> None:

        self.strategy: Strategy = strategy
        self.connection: BlockingConnection = queue_connection
        self.channel: BlockingChannel = self.connection.channel()
        self.client_manager: ClientManager = ClientManager()

        self.tmp = "./tmp/"

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

                    # get the local params from s3
                    download(file_name=decoded_msg.param_link, local_path=self.tmp + decoded_msg.param_link)

                    # update client stage
                    self.client_manager.update_local_params(decoded_msg)

            """------------------------Checking for update-------------------------------"""
            # Check the update condition asynchronously
            finished_clients = self.client_manager.filter_finished_clients_by_epoch(self.strategy.current_epoch)

            # if the update condition is true
            if self.strategy.check_update(len(finished_clients)):
                params_to_update = []
                join_clients = []
                cli: Client

                # Get all finished clients in the current epoch
                for cli in finished_clients:
                    params_to_update.append(cli.params_link)
                    join_clients.append(cli)

                # Update 
                self.strategy.aggregate(params_to_update, join_clients)

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
        global_params_link = self.strategy.initialize_parameters()

        # select clients
        chosen_id = self.strategy.select_client(selected_clients)

        # create msg object
        msg = GlobalMessage(chosen_id, self.strategy.current_epoch, global_params_link)

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
