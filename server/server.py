from abc import ABC, abstractmethod
import pika 
from pika.adapters.blocking_connection import BlockingChannel




class Server(ABC):

    @abstractmethod
    def start(self):
        """
        Start to listen to events from queue server.
        """
    @abstractmethod
    def stop(self):
        """Stop training and release resource
        """


    @abstractmethod
    def redirect(self):
        """Redirect the message to the target function by routing key.
        """


    @abstractmethod
    def translate_message(self):
        """Translate messages in rabbitmq to the target type
        """


    def new_round(self):
        """Start new round
        """


    @abstractmethod
    def check_available_clients(self):
        """Check if worker available before training process
        """

    @abstractmethod
    def send_parameters(self):
        """send the global parameters to clients.
        """

