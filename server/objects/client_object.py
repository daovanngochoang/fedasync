import numpy as np



class Client:
    def __init__(self, id) -> None:
        self.id : str = id
        self.current_epoch : int
        self.local_weights : np.array
        self.is_finish : bool
        self.accuracy : float
        self.start_time : str
        self.finish_time : str
