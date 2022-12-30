from abc import ABC, abstractmethod
from typing import Dict, List

from commons.utils.weight_file_helpers import load_nparray_from_file, save_nparray_to_file
from strategy import Strategy
from commons.objects.client import Client
from commons.config import ServerConfig
import numpy as np


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
            weight_file = ServerConfig.TMP_FOLDER + cli.weight_file
            bias_file = ServerConfig.TMP_FOLDER + cli.bias_file
            weight = load_nparray_from_file(weight_file)
            bias = load_nparray_from_file(bias_file)

            if len(total_weight) == 0:
                total_weight = weight
                total_bias = bias
            else:
                total_weight += weight
                total_bias += bias

        total_clients = len(join_clients)
        avg_weight = total_weight / total_clients
        avg_bias = total_bias / total_clients
        save_nparray_to_file(avg_weight, self.global_weight_file)
        save_nparray_to_file(avg_bias, self.global_bias_file)

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def save_weight_and_bias_to_file(self):
        pass
