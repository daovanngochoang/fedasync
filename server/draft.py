
from server.objects.client_object import Client
from strategies.strategy import Strategy
from client_manager import ClientManager
from utils import time_diff, time_now



class ProcessManager:
    
    
    def __init__(self,  strategy : Strategy, 
                    n_epochs : int = 3,
                    min_update_clients : int = 3,
                    min_fit_clients : int = 3, 
                    convergent_value : int = 0.1,
                    time_ratial : float = 0.5
                    ) -> None:
        
        # the minimum clients to start training process
        self.strategy : Strategy  = strategy
        
        # the minimum clients to start training process
        self.min_fit_clients =  min_fit_clients 
        self.min_update_clients = min_update_clients
        self.n_epochs = n_epochs
        self.time_ratial = time_ratial

        # current server epoch
        self.current_epoch : int = 0
        
        # Client manager
        self.client_manager : ClientManager = ClientManager()
        
        # the convergent condition value
        self.convergent_value : float = convergent_value 
        
        # starting time of the training process
        self.start_time : str = ""
        self.first_finished = ""
        self.latest_finished = ""




    def get_params(self):
        return self.strategy.initialize_parameters()


    def selected_clients(self):
        all_clients = self.client_manager.get_all()
        result = self.strategy.select_client(all_clients)
        return result


    def start_condition(self) -> bool:
        n_clients = self.client_manager.get_available()
        return n_clients > self.min_fit_clients 


    def update_condition(self) -> bool:
        finished_clients = self.client_manager.filter_finished_clients_by_epoch()

        total_finished = len(finished_clients)

        if (self.start_time != self.first_finished != self.latest_finished != ""):
            t1 = time_diff(self.start_time, self.first_finished)
            t2 = time_diff(self.start_time, self.latest_finished)
            
            # get avg complete time
            avg = (t2 + t1)/total_finished
            time_cond = avg + (self.time_ratial*avg)

            # get time up to now
            now = time_now()
            until_now = time_diff(self.start_time, now)

        return  time_cond > until_now or total_finished == self.min_update_clients

    def stop_condition(self):

        return  self.current_epoch == self.n_epochs 

    def manage_update(self):
        
        """Control update 
        """

        """
            Check update condition including:
            1. min clients to update
            2. 
        """

        if self.update_condition: 
            self.strategy.aggregate()


       



    

       