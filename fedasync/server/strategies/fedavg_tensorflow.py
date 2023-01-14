from abc import abstractmethod

import numpy as np

from fedasync.commons.utils import save_array
from fedasync.server.strategies import FedAvg


class FedAvgTensorflow(FedAvg):

    def __init__(self, model, n_epochs: int, min_update_clients: int, min_fit_clients: int,
                 convergent_value: float):
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value)

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def data_preprocessing(self):
        pass

    def set_model_weights(self, weights):
        self.model.set_weights(weights)

    def get_model_weights(self) -> None:
        prams = self.model.get_weights()
        save_array(np.array(prams, dtype=object), self.path_to_weights_file)
