import numpy as np

from fedasync.commons.utils import save_array
from fedasync.server.strategies import FedAvg


class FedAvgTensorflow(FedAvg):

    def __init__(self, model, n_epochs: int = 3, min_update_clients: int = 3, min_fit_clients: int = 3,
                 convergent_value: float = 0.1):
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value)


    def evaluate(self):
        pass

    def get_model_weights(self) -> None:
        prams = self.model.get_weights()
        save_array(np.array(prams, dtype=object), self.path_to_weights_file)
