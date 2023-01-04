from abc import ABC, abstractmethod
from typing import List, Dict

from fedasync.commons import Config
from fedasync.commons.objects.client import Client
import uuid


class Strategy(ABC):

    def __init__(self,
                 model,
                 n_epochs: int,
                 min_update_clients: int,
                 min_fit_clients: int,
                 convergent_value: float,
                 ) -> None:
        self.id = str(uuid.uuid4())
        self.global_weights_file: str = "{}.weights.npy".format(self.id)

        self.model = model
        # the minimum clients to start training process
        self.min_fit_clients = min_fit_clients
        self.min_update_clients = min_update_clients
        self.n_epochs = n_epochs

        # current server epoch
        self.current_epoch: int = 0

        # the convergent condition value
        self.convergent_value: float = convergent_value

        self.tmp = Config.TMP_FOLDER
        self.path_to_weights_file = self.tmp + self.global_weights_file
        
        print("\n\n------------------------------START FEDASYNC------------------------------------------\n\n")

        print("Min number of clients condition to start training: ",self.min_fit_clients)
        print("Min number of clients to start aggregating: ", self.min_update_clients)

    def initialize_parameters(self):
        """Initialize the global parameters.
        """
        print("Initialize the global parameters.")
        return self.global_weights_file

    @abstractmethod
    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        """ Implement the client selection logic by 
        """

    @abstractmethod
    def aggregate(self, join_clients: Dict[str, Client]) -> None:
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    @abstractmethod
    def get_model_weights(self):
        """
        """

    def is_min_clients_completed(self, total_finished: int):
        return total_finished >= self.min_update_clients

    def start_condition(self, available_clients) -> bool:
        return available_clients >= self.min_fit_clients

    def is_finish(self):
        return self.n_epochs - self.current_epoch <= 0
