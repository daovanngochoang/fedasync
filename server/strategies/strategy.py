
from abc import ABC, abstractmethod
from server.objects.client_object import Client


class Strategy(ABC):


    def initialize_parameters(self):
        """Initialize the global parameters.
        """

    def client_selection(self) -> list[Client.id]:
        """ Implement the client selection logic by 
        """
    
    @abstractmethod
    def aggregate(self):
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    def check_update(self):
        """Check the update condition
        """

    def is_finish(self):
        """Check if the training process is finish
        """

    def save_local_parameters(self):
        """Save local parameters before aggregate
        """
    
    def update_client_state(self):
        """Update client info
        """
    
    def manage_process(self, msg):
        """Receive message and manage updating process
        """

    

