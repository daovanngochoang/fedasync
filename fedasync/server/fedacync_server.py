from fedasync.commons.config import *
from fedasync.commons.objects import Client
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
import sys, os
from fedasync.commons.utils import *
from fedasync.server import ClientManager
from fedasync.server.strategies import Strategy


class Server:

    def __init__(self, strategy: Strategy, queue_connection: BlockingConnection, time_rational: float = 0.5,
                 time_out: int = None) -> None:

        self.strategy: Strategy = strategy
        self.connection: BlockingConnection = queue_connection

        self.channel: BlockingChannel = self.connection.channel()
        self.client_manager: ClientManager = ClientManager()
        self.awss3 = AwsS3()
        self.time_out = time_out
        self.time_rational = time_rational
        # starting time of the training process
        self.start_time: str = ""
        self.first_finished: str = ""
        self.latest_finished: str = ""

    def get_msg(self):
        method_frame: Basic.GetOk
        header_frame: BasicProperties
        method_frame, header_frame, body = self.channel.basic_get(QueueConfig.SERVER_QUEUE)
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
        return method_frame, header_frame, body

    def start(self):

        # connect to queue server and create queue
        self.setup()


        try:
            while True:
                method_frame: Basic.GetOk
                header_frame: BasicProperties
                method_frame, header_frame, body = self.get_msg()

                # Listen to server queue and get all register message
                while method_frame:
                    routing_key = method_frame.routing_key
                    if routing_key == RoutingRules.CLIENTS_REGISTER:
                        new_client = Client(id=body.decode())
                        self.client_manager.add_client(new_client)

                        print("{} of clients {} joined".format(self.client_manager.total(), self.strategy.min_fit_clients))
                        # print(self.client_manager.get_clients_to_list())

                        method_frame, header_frame, body = self.get_msg()

                # get all available
                n_available = self.client_manager.total()

                # if enough clients => start training
                if self.strategy.start_condition(n_available):
                    print("\n\n")
                    print("START TRAINING ...")
                    self.train()
                    break

        except KeyboardInterrupt:
            print('Interrupted')
            try:
                self.stop()
                sys.exit(0)
            except SystemExit:
                os._exit(0)

    def train(self):
        """
        Start training distributed on multiple workers
        """

        # start new epoch
        self.strategy.get_model_weights()
        self.new_epoch()

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
                    print("RECEIVE UPDATE")
                    # decode msg to rabbitmq msg
                    decoded_msg = decode_update_msg(body)

                    # get the weight and bias from s3
                    self.awss3.download_awss3_file(file_name=decoded_msg.weight_file)

                    # record the time
                    if (self.first_finished and self.latest_finished) == "":
                        now = time_now()
                        self.first_finished = now
                        self.latest_finished = now
                    elif self.first_finished != "":
                        self.latest_finished = time_now()

                    # update client stage
                    self.client_manager.update_local_params(decoded_msg)
                    # print(self.client_manager.get_clients_to_list())
                    print("Completed Clients", len(self.client_manager.filter_finished_clients_by_epoch(self.strategy.current_epoch)))

            """------------------------Checking for update-------------------------------"""
            # Check the update condition asynchronously
            finished_clients = self.client_manager.filter_finished_clients_by_epoch(self.strategy.current_epoch)

            # if the update condition is true
            if self.strategy.is_min_clients_completed(len(finished_clients)):

                # get time from start to first and latest finished client
                t1 = time_diff(self.start_time, self.first_finished)
                t2 = time_diff(self.start_time, self.latest_finished)

                # get avg complete time
                avg = (t2 + t1) / len(finished_clients)

                # get time bound
                time_bound = avg + (self.time_rational * avg)

                # get time up to now
                now = time_now()
                until_now = time_diff(self.start_time, now)

                # if until now > time bound => update
                time_cond = until_now > time_bound

                if time_cond:

                    # Update
                    print("AGGREGATE \n")
                    self.strategy.aggregate(finished_clients)

                    # Save value to history
                    self.client_manager.save_history(self.strategy.current_epoch)

                    # If training process is done => break
                    if self.strategy.is_finish():
                        print("STOP TRAINING")
                        self.stop()
                        break
                    # if training process is not finished => new epoch
                    elif not (self.strategy.is_finish()):
                        print("NEW ROUND")
                        self.new_epoch()

            if self.time_out is not None and len(finished_clients) == 0:
                until_now = time_diff(self.start_time, time_now())
                if until_now > self.time_out:
                    print("TIME OUT!")
                    self.stop()
                    break

    def new_epoch(self):

        self.start_time = time_now()
        self.first_finished = ""
        self.latest_finished = ""
        self.strategy.current_epoch += 1

        # Generate new params
        global_weight_file = self.strategy.initialize_parameters()

        # upload latest global model
        self.awss3.upload_file_to_awss3(global_weight_file)

        # select clients
        chosen_id = self.strategy.select_client(self.client_manager.get_all())

        self.client_manager.make_available(chosen_id)

        # update min update.
        if self.strategy.current_epoch > 1:
            self.strategy.min_update_clients = int(len(chosen_id) / 2)

        # create msg object
        msg = GlobalMessage(chosen_id=chosen_id, current_epoch=self.strategy.current_epoch,
                            n_epochs=self.strategy.n_epochs,
                            weight_file=global_weight_file)

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
        self.channel.exchange_declare(QueueConfig.EXCHANGE, exchange_type="direct")

        # binding server queue to the related routing key in queue config.
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

        # Delete old msg in the queue
        self.channel.queue_purge(QueueConfig.CLIENT_QUEUE)
        # Delete old msg in the queue
        self.channel.queue_purge(QueueConfig.SERVER_QUEUE)

    def send_to_clients(self, routing_key: str, body) -> None:
        """Send message with routing key
        """
        print("Send to all Clients")
        self.channel.basic_publish(
            exchange=QueueConfig.EXCHANGE,
            routing_key=routing_key,
            body=body)
