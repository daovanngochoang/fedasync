

from server.objects.client_object import Client
import numpy as np



class  ClientManager:
    def __init__(self) -> None:
        
        self.client_pools = dict[Client.id, Client]
        self.history_state = dict[int, dict[str, Client]]
        

    def add_client(self, client : Client) -> None:
        self.client_pools[client.id] = client


    def total(self):
        return len(self.client_pools)


    def get_all(self) -> dict[Client.id, Client]:
        return self.client_pools


    def filter_by_epoch(self, epoch : int) -> dict[str, Client]:
        result : dict[str, Client] = {}
        client : Client

        for client in self.client_pools:
            if client.id == epoch:
                result[client.id] = client

        return result


    def filter_finished_clients_by_epoch(self, epoch : int) -> dict[str, Client]:
        """Filter out all clients that finished training on the input epoch
        """
        result : dict[str, Client]
        client : Client

        for client in self.client_pools:
            if client.id == epoch and client.available == True:
                result[client.id] = client
        
        return result
        

    def increase_epoch(self, id : Client.id) -> None:
        """Update client's epoch 
        """
        # if that client exit 
        if self.client_pools[id] != None:
            self.client_pools[id].current_epoch += 1


    def new_epoch_state(self, id : str, time : str):
        """Update client starting time
        """
        # if that client exit 
        if self.client_pools[id] != None:
            self.client_pools[id].start_time = time
            self.client_pools[id].current_epoch += 1
            self.client_pools[id].available = False


    
    def update_local_params(self, id : Client.id, params: np.ndarray , finish_time : str, acc : float, 
                        loss : float, available : bool) -> None:
        """Update client state when the local params are updated to server
        """
        if self.client_pools[id] != None:
            self.client_pools[id].local_params = params
            self.client_pools[id].acc = acc
            self.client_pools[id].loss = loss
            self.client_pools[id].finish_time = finish_time
            self.client_pools[id].available = True


    def get_available(self):
        n_available = 0
        client : Client
        for client in self.client_pools:
            if client.available:
                n_available += 1
        
        return n_available
    
    def save_history(self, epoch: int):
        self.history_state[epoch] = self.client_pools


    def reset_client_pools(self):
        client : Client
        for client in self.client_pools:
            self.update_state(
                id = client.id,
                params=None,
                start_time="",
                finish_time="",
                loss=1,
                acc=0)