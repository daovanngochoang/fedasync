
from queue_config import *
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties


class QueueManager:

    def __init__(self, connection : BlockingConnection, 
                        routing_rules : RoutingRules,
                        queue_config : QueueConfig
                        ) -> None:

        self.connection : BlockingConnection = connection
        self.channel : BlockingChannel = self.connection.channel()
        self.routing_rules : RoutingRules = routing_rules
        self.queue_config : QueueConfig = queue_config


    def setup(self) -> None:
        """Connect to queue server and create queue, setup binding key, exchange for queue
        """
        # create server and client queue.
        self.channel.queue_declare(self.queue_config.SERVER_QUEUE)
        self.channel.queue_declare(self.queue_config.CLIENT_QUEUE)

        # create exchange
        self.channel.exchange_declare(self.queue_config.EXCHANGE, exchange="direct")
    
        # binding server queue to the related reouting key in queue config.
        self.channel.queue_bind(
            queue=self.queue_config.SERVER_QUEUE, 
            exchange = self.queue_config.EXCHANGE, 
            routing_key=self.routing_rules.LOCAL_UPDATE)
        
        self.channel.queue_bind(
            queue=self.queue_config.SERVER_QUEUE, 
            exchange = self.queue_config.EXCHANGE, 
            routing_key=self.routing_rules.AVAILABLE_CLIENT_RESPONE)
        
        self.channel.queue_bind(
            queue=self.queue_config.SERVER_QUEUE, 
            exchange = self.queue_config.EXCHANGE, 
            routing_key=self.routing_rules.RECEIVED_NOTIFY)


        # binding client queue to it's routing key in queue config
        self.channel.queue_bind(
            queue=self.queue_config.CLIENT_QUEUE, 
            exchange = self.queue_config.EXCHANGE, 
            routing_key=self.routing_rules.NEW_EPOCH)

        self.channel.queue_bind(
            queue=self.queue_config.CLIENT_QUEUE, 
            exchange = self.queue_config.EXCHANGE, 
            routing_key=self.routing_rules.CHECK_AVAILABLE_CLIENT)



    def send_to_clients(self, routing_key : str, body : str) -> None:
        """Send message with routing key
        """
        self.channel.basic_publish( 
            exchange = self.queue_config.EXCHANGE, 
            routing_key = routing_key, 
            body = body)