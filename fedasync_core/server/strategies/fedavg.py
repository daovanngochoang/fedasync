from abc import ABC, abstractmethod
from typing import Dict, List

from fedasync_core.commons.objects.client import Client
from fedasync_core.commons.config import Config
import numpy as np

from fedasync_core.commons.utils.numpy_file_helpers import load_array, save_array
from fedasync_core.server.strategies.strategy import Strategy


class FedAvg(Strategy, ABC):

    def __init__(self, model, n_epochs: int = 3, min_update_clients: int = 3, min_fit_clients: int = 3,
                 convergent_value: float = 0.1, time_rational: float = 0.5) -> None:
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value, time_rational)

    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        return [x for x in all_clients]

    def aggregate(self, join_clients: Dict[str, Client]):
        """Aggregate algorithm, update to the global model
        """
        total_weight: np.ndarray = np.array([])

        for cli_id in join_clients:
            weight_file = join_clients[cli_id].weight_file

            # Load the array from the specified file using the numpy.load function
            weight = load_array(self.tmp + weight_file)

            if len(total_weight) == 0:
                total_weight = weight
            else:
                for layers in range(len(weight)):
                    total_weight[layers] += weight[layers]

        total_clients = len(join_clients)
        avg_weights = total_weight / total_clients
        save_array(avg_weights, self.path_to_weights_file)

    @abstractmethod
    def evaluate(self):
        pass


