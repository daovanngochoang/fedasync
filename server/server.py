
from queue_config import *
from server.objects.client_object import Client
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
from utils import *
from server.draft.queue_manager import *
from client_manager import ClientManager
import json
import numpy as np
import sys, os





class Server:

    def __init__(self, strategy : Strategy, queue_connection : BlockingConnection ) -> None:
        
        self.strategy : Strategy  = strategy
        self.connection : BlockingConnection = queue_connection
        self.channel : BlockingChannel = self.connection.channel()
        self.client_manager : ClientManager = ClientManager()

  


    def get_msg(self):
        method_frame, header_frame, body = self.channel.basic_get(QueueConfig.SERVER_QUEUE)
        self.channel.basic_ack(method_frame.delivery_tag)
        return method_frame, header_frame, body
  
  
    def start(self):
        
        try:
            while True:
                # connect to queue server and create queue
                self.setup()
                
                method_frame :  Basic.GetOk
                header_frame: BasicProperties

                method_frame, header_frame, body = self.get_msg()

                # Listen to server queue and get all register message
                while (method_frame):
                    routing_key = method_frame.routing_key
                    if (routing_key == RoutingRules.CLIENTS_REGISTER):
                        new_client = Client(id = body.decode())
                        self.client_manager.add_client(new_client)

                        method_frame, header_frame, body = self.get_msg()


                # notify to clients
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
        Start to listen to events from queue server.
        """
        # start new epoch
        self.new_epoch()

        while True:
            method_frame :  Basic.GetOk
            header_frame: BasicProperties

            # Get msg and redirect
            method_frame, header_frame, body = self.get_msg()

            if (method_frame):
                routing_key   = method_frame.routing_key

                # update prams routing key
                if routing_key == RoutingRules.LOCAL_UPDATE:
                    
                    # EDIT LATER
                    decoded_msg = decode_update_params(body)

                    self.client_manager.update_local_params(
                        id=decoded_msg["id"],
                        epoch=decoded_msg["epoch"],
                        params=decoded_msg["params"],
                        start_time=decoded_msg["start"],
                        finish_time=decoded_msg["end"],
                        acc=decoded_msg["acc"],
                        loss=decoded_msg["loss"]
                    )


            # Check the update condition asynchronously
            finished_clients =  self.client_manager.filter_finished_clients_by_epoch(self.strategy.current_epoch)
            
            # if the update condition is true
            if self.strategy.check_update(finished_clients) == True:
                all_params = []
                cli : Client

                # Get all finished clients in the current epoch
                for cli in finished_clients:
                    all_params.append(cli.local_params)

                # Update 
                self.strategy.aggregate(all_params)

                # Save value to history
                self.client_manager.save_history(self.strategy.current_epoch)
                
                # if training process is not finished => new epoch
                if not (self.strategy.is_finish()):
                    self.new_epoch()

                # If training process is done => break
                elif self.strategy.is_finish():
                    self.stop()
                    break
        

    def new_epoch(self):
        # Generate new params
        new_params = self.strategy.initialize_parameters()
        # Send new generated params
        self.channel.queue_purge(QueueConfig.CLIENT_QUEUE)
        self.send_params(new_params)



    def send_params(self, params : np.ndarray):
        """Send params to clients
        """
        # generate params
        # Encode msg 
        # Send
        


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
            exchange = QueueConfig.EXCHANGE, 
            routing_key=RoutingRules.LOCAL_UPDATE)
        
        self.channel.queue_bind(
            queue=QueueConfig.SERVER_QUEUE, 
            exchange = QueueConfig.EXCHANGE, 
            routing_key=RoutingRules.AVAILABLE_CLIENT_RESPONSE)
        
        self.channel.queue_bind(
            queue=QueueConfig.SERVER_QUEUE, 
            exchange = QueueConfig.EXCHANGE, 
            routing_key=RoutingRules.RECEIVED_NOTIFY)


        # binding client queue to it's routing key in queue config
        self.channel.queue_bind(
            queue=QueueConfig.CLIENT_QUEUE, 
            exchange = QueueConfig.EXCHANGE, 
            routing_key=RoutingRules.NEW_EPOCH)

        self.channel.queue_bind(
            queue=QueueConfig.CLIENT_QUEUE, 
            exchange = QueueConfig.EXCHANGE, 
            routing_key=RoutingRules.CHECK_AVAILABLE_CLIENT)





    def send_to_clients(self, routing_key : str, body : str) -> None:
        """Send message with routing key
        """
        self.channel.basic_publish( 
            exchange = QueueConfig.EXCHANGE, 
            routing_key = routing_key, 
            body = body)

