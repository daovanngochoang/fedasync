
from queue_config import *
from strategies.strategy import Strategy
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties


class QueueManager:

    def __init__(self, connection : BlockingConnection) -> None:

        self.connection : BlockingConnection = connection
        self.channel : BlockingChannel = self.connection.channel()



    def setup(self) -> None:
        """Connect to queue server and create queue, setup binding key, exchange for queue
        """
        # create server and client queue.
        self.channel.queue_declare(QueueConfig.SERVER_QUEUE)
        self.channel.queue_declare(QueueConfig.CLIENT_QUEUE)

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