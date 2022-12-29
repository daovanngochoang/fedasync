class GlobalMessage:
    def __init__(self, chosen_id: list, epoch: int, param_link: str):
        self.chosen_id = chosen_id
        self.epoch = epoch
        self.param_link = param_link


class UpdateMessage:
    def __init__(self, client_id: str, epoch: int, param_link: str
                 , acc: float, loss: float, start: str, end: str):
        self.client_id = client_id
        self.epoch = epoch
        self.param_link = param_link
        self.acc = acc
        self.loss = loss
        self.start = start
        self.end = end


