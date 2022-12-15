

from server.objects.client_object import Client
import numpy as np



class  ClientManager:
    def __init__(self) -> None:
        
        self.client_pools = dict[Client.id, Client]
        self.history_state = dict[int, dict[str, Client]]
        

    def add_client(self, client : Client) -> None:
        """Add new clients
        """
        self.client_pools[client.id] = client


    def total(self):
        """Get total clients number
        """
        return len(self.client_pools)


    def get_all(self) -> dict[Client.id, Client]:
        """Get all clients
        """
        return self.client_pools


    def filter_by_epoch(self, epoch : int) -> dict[str, Client]:
        """Filter all clients are training in the current epoch.
        """
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


    
    def update_local_params(self, id : Client.id, epoch:int ,params: np.ndarray, start_time: str, finish_time : str, acc : float, 
                        loss : float) -> None:
        """Update client state when the local params are updated to server
        """
        if self.client_pools[id] != None:
            self.client_pools[id].local_params = params
            self.client_pools[id].current_epoch = epoch
            self.client_pools[id].acc = acc
            self.client_pools[id].loss = loss
            self.client_pools[id].start_time = start_time
            self.client_pools[id].finish_time = finish_time
            self.client_pools[id].is_finished = True


    def get_available(self):
        """Get available clients in the pool
        """
        n_available = 0
        client : Client
        for client in self.client_pools:
            if client.available:
                n_available += 1
        
        return n_available
    
    def save_history(self, epoch: int):
        """Save the history states of clients over epochs that help to the analytic approaches
        """
        self.history_state[epoch] = self.client_pools


    def reset_client_pools(self):
        """Reset client state 
        """
        client : Client
        for client in self.client_pools:
            client.reset()