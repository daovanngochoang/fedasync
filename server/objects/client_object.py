import numpy as np



class Client:
    def __init__(self, id : str) -> None:
        self.id : str = id
        self.current_epoch : int = 0
        self.local_params : np.array = None
        self.acc : float = 0.0
        self.start_time : str = None
        self.finish_time : str = None
        self.loss: float = 1.0
        self.available : bool = True
        
