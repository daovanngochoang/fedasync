from strategy import Strategy
from client_manager import ClientManager
from server.objects.client_object import Client
import numpy as np 
from abc import ABC, abstractmethod


class FedAvg(Strategy):

    def __init__(self, model) -> None:

        self.global_params : np.ndarray

        self.global_model = model

    
    def initialize_parameters(self):
        """Initialize the global parameters.
        """


    def client_selection(self, all_clients : dict[str, Client]) -> list[Client.id]:
        """ Implement the client selection logic by 
        """
    
    def aggregate(self, all_clients : dict[str, Client]) -> None:
        """Aggregate algorithm, update to the global model
        """

    def evaluate(self):
        """Evaluate the current parameters
        """

    def check_update(self):
        """Check the update condition
        """