import numpy as np

from fedasync_core.commons.utils.awss3_file_manager import AwsS3 as wf
from fedasync_core.commons.utils.numpy_file_helpers import save_array
from fedasync_core.server.strategies.fedavg import FedAvg


class FedAvgTensorflow(FedAvg):

    def __init__(self, model, n_epochs: int = 3, min_update_clients: int = 3, min_fit_clients: int = 3,
                 convergent_value: float = 0.1, time_rational: float = 0.5):
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value, time_rational)
        print(self.min_update_clients)
        print(self.min_fit_clients)

    def evaluate(self):
        pass

    def get_model_weights(self) -> None:
        prams = self.model.get_weights()
        save_array(np.array(prams, dtype=object), self.path_to_weights_file)
