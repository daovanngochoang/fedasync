class Client:
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.current_epoch: int = 0
        self.weight_file = ""
        self.acc: float = 0.0
        self.start_time: str = ""
        self.finish_time: str = ""
        self.loss: float = 1.0
        self.is_finished: bool = True

    def reset(self):
        self.current_epoch = 0
        self.weight_file = ""
        self.acc = 0.0
        self.start_time = ""
        self.finish_time = ""
        self.loss = 1.0
        self.is_finished = False
