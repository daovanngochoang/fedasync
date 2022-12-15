
from abc import ABC, abstractmethod
from server.objects.client_object import Client
import numpy as np
from client_manager import ClientManager
from utils import time_diff, time_now




class Strategy(ABC):
    
    def __init__(self,  
                    init_params, 
                    n_epochs : int = 3,
                    min_update_clients : int = 3,
                    min_fit_clients : int = 3, 
                    convergent_value : int = 0.1,
                    time_rational : float = 0.5
                    ) -> None:

        self.global_params : np.ndarray = init_params

         # the minimum clients to start training process
        self.min_fit_clients =  min_fit_clients 
        self.min_update_clients = min_update_clients
        self.n_epochs = n_epochs
        self.time_rational = time_rational

        # current server epoch
        self.current_epoch : int = 0
        
        # the convergent condition value
        self.convergent_value : float = convergent_value 
        
        # starting time of the training process
        self.start_time : str = ""
        self.first_finished : str = ""
        self.latest_finished : str= ""



    # 
    def initialize_parameters(self):
        """Initialize the global parameters.
        """
        self.start_time = time_now()
        self.first_finished = ""
        self.latest_finished = ""
        return self.global_params


    @abstractmethod
    def select_client(self) -> list[Client.id]:
        """ Implement the client selection logic by 
        """
    
    @abstractmethod
    def aggregate(self, local_params : list[np.ndarray]) -> None:
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    # @abstractmethod
    def check_update(self, finished_clients):
        """Check the update condition
            1. We wait until 50% of clients are finished
            2. After 50% clients finished => We use the time measurement technique
            3. We also check the min clients to update simultaneously 
        """
        # finished_clients = self.client_manager.filter_finished_clients_by_epoch(self.current_epoch)

        total_finished = len(finished_clients)

        if (self.start_time != self.first_finished != self.latest_finished != ""):
            t1 = time_diff(self.start_time, self.first_finished)
            t2 = time_diff(self.start_time, self.latest_finished)
            
            # get avg complete time
            avg = (t2 + t1)/total_finished
            time_cond = avg + (self.time_rational*avg)

            # get time up to now
            now = time_now()
            until_now = time_diff(self.start_time, now)

        return  time_cond > until_now or total_finished == self.min_update_clients



    def start_condition(self, available_clients) -> bool:
        return available_clients > self.min_fit_clients


    def is_finish(self):
        return self.current_epoch == self.n_epochs





