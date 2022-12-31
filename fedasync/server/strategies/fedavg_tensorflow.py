from server.strategies.fedavg import FedAvg
from commons.utils.weight_file_helpers import save_nparray_to_file


class FedAvgTensorflow(FedAvg):
    def __init__(self, model, n_epochs: int = 3, min_update_clients: int = 3, min_fit_clients: int = 3,
                 convergent_value: float = 0.1, time_rational: float = 0.5):
        super().__init__(model, n_epochs, min_update_clients, min_fit_clients, convergent_value, time_rational)

    def evaluate(self):
        pass

    def save_weight_and_bias_to_file(self):
        # get weight and bias of the model
        weight, bias = self.model.get_weights()

        # save to file
        save_nparray_to_file(weight, self.global_weight_file)
        save_nparray_to_file(bias, self.global_bias_file)
