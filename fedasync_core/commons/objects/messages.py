class GlobalMessage:
    def __init__(self, chosen_id: list, current_epoch: int, n_epochs: int, weight_file: str):
        self.chosen_id = chosen_id
        self.current_epoch = current_epoch
        self.n_epochs = n_epochs
        self.weight_file = weight_file


class UpdateMessage:
    def __init__(self, client_id: str, epoch: int, weight_file: str
                 , acc: float, loss: float, start: str):
        self.client_id = client_id
        self.epoch = epoch
        self.weight_file = weight_file
        self.acc = acc
        self.loss = loss
        self.start = start


