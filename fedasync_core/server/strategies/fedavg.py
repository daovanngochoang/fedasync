from abc import ABC, abstractmethod
from typing import Dict, List

from fedasync_core.commons.objects.client import Client
from fedasync_core.commons.config import ServerConfig
import numpy as np
from fedasync_core.server.strategies.strategy import Strategy


class FedAvg(Strategy, ABC):

    def __init__(self, model, n_epochs: int = 3,
                 min_update_clients: int = 3,
                 min_fit_clients: int = 3,
                 convergent_value: float = 0.1,
                 time_rational: float = 0.5) -> None:
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value, time_rational)

    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        return [x for x in all_clients]

    def aggregate(self, join_clients: List[Client]) -> None:
        """Aggregate algorithm, update to the global model
        """
        total_weight: np.ndarray = np.array([])
        total_bias: np.ndarray = np.array([])

        for cli in join_clients:
            weight_file = self.tmp + cli.weight_file
            bias_file = self.tmp + cli.bias_file

            # Load the array from the specified file using the numpy.load function
            weight = np.load(self.tmp + weight_file)
            bias = np.load(self.tmp + bias_file)

            if len(total_weight) == 0:
                total_weight = weight
                total_bias = bias
            else:
                total_weight += weight
                total_bias += bias

        total_clients = len(join_clients)
        avg_weight = total_weight / total_clients
        avg_bias = total_bias / total_clients
        self.save_weight_and_bias_to_file(avg_weight, avg_bias)

    @abstractmethod
    def evaluate(self):
        pass


