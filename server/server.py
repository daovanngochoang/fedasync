
from queue_config import *
from server.objects.client_object import Client
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties
from utils import *
from queue_manager import *
from client_manager import ClientManager
import json

class Server:

    def __init__(self, strategy : Strategy, queue_connection : BlockingConnection ) -> None:
        
        self.queue_config : QueueConfig = QueueConfig()        
        self.routing_rules : RoutingRules = RoutingRules()
        self.strategy : Strategy  = strategy

        self.connection : BlockingConnection = queue_connection
        self.channel : BlockingChannel = self.connection.channel()

        self.queue_manager : QueueManager = QueueManager(queue_connection, self.routing_rules, self.queue_config)
        self.client_manager : ClientManager = ClientManager()



    def start(self):
        """
        Start to listen to events from queue server.
        """

        # connect to queue server and create queue
        self.queue_manager.setup()

        #check if enough client to start training
        
        
        while True:
            method_frame :  Basic.GetOk
            header_frame: BasicProperties

            # Get msg and redirect
            method_frame, header_frame, body = self.channel.basic_get(self.queue_config.SERVER_QUEUE)
            if (method_frame):
                routing_key   = method_frame.routing_key
                self.redirect(routing_key, body)

            # check the update condition asynchronously
            self.strategy.manage_update()


    def send_params(self):
        # generate params
        params = self.strategy.initialize_parameters()
        
        encoded_params = encode_params(params)

        msg = ""

        self.queue_manager.send_to_clients(msg)


    def stop(self):
        """Stop training and release resource
        """
        self.channel.close()
        self.connection.close()




    

    def translate_message(self, msg_body):
        """Translate messages in rabbitmq to the target type

        input: msg body
        output: m
        """

        return 



    def redirect(self, routing_key, msg_body):

        if (routing_key == self.routing_rules.LOCAL_UPDATE):
            print("local update")
            decoded = decode_update_params()
            self.client_manager.update_local_params()

        elif (routing_key == self.routing_rules.RECEIVED_NOTIFY):
            print("received model!")
            decoded = decode_message()
            self.client_manager.new_epoch_state()

        elif (routing_key == self.routing_rules.AVAILABLE_CLIENT_RESPONE):
            print("Register")
            decoded = decode_message()
            
            new_client = Client(id = "id here!!")
            self.client_manager.add_client(new_client)




    def new_round(self):
        """Start new round
        """
        new_params = self.strategy.initialize_parameters()
        self.send_parameters(new_params)


    def check_available_clients(self):
        """Check if worker available before training process
        """

    def send_parameters(self, params):
        """send the global parameters to clients.
        """


