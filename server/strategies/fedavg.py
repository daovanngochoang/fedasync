from typing import Dict, List

from commons.utils.weight_file_helpers import load_nparray_from_file, save_nparray_to_file
from strategy import Strategy
from commons.objects.client_object import Client
from commons.config import ServerConfig
import numpy as np


class FedAvg(Strategy):

    def __init__(self, params_file: str, n_epochs: int = 3,
                 min_update_clients: int = 3,
                 min_fit_clients: int = 3,
                 convergent_value: int = 0.1,
                 time_rational: float = 0.5) -> None:
        super().__init__(params_file, n_epochs, min_update_clients, min_fit_clients, convergent_value, time_rational)

    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        return [x for x in all_clients]

    def aggregate(self, local_param_links: List[str], join_clients: List[Client]) -> None:
        """Aggregate algorithm, update to the global model
        """
        total_weights: np.ndarray = np.array([])
        for link in local_param_links:
            file_path = ServerConfig.TMP_FOLDER + link
            local_weight = load_nparray_from_file(file_path)

            if len(total_weights) == 0:
                total_weights = local_weight
            else:
                total_weights += local_weight

        total_clients = len(join_clients)
        avg_weights = total_weights / total_clients
        save_nparray_to_file(avg_weights, self.global_params_file)

    def evaluate(self):
        pass