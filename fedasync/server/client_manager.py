import json
import os
from typing import Dict
from fedasync.commons.config import Config
from fedasync.commons.objects import UpdateMessage
from fedasync.commons.objects import Client
from fedasync.commons.utils import time_now


class ClientManager:
    def __init__(self) -> None:
        """Initialize a ClientManager object.

        The client_pools attribute is a dictionary of Client objects,keyed by client id.
        The history_state attribute is a dictionary that maps epoch numbers
        to dictionaries of Client objects, keyed by client id.
        """
        self.client_pools: Dict[str, Client] = {}
        self.history_state: Dict[int, Dict[str, Client]] = {}

    def add_client(self, client: Client) -> None:
        """Add a client to the client_pools attribute.

        Args:
            client (Client): The Client object to add.
        """
        # Add the client to the client_pools dictionary
        self.client_pools[client.id] = client

    def total(self):
        """Get the total number of clients.

        Returns:
            int: The number of clients in the client_pools attribute.
        """
        return len(self.client_pools)

    def get_all(self) -> Dict[str, Client]:
        """Get all clients from the client_pools attribute.

        Returns:
           Dict[str, Client]: A dictionary of all Client objects in the
               client_pools attribute, keyed by client id.
        """
        return self.client_pools

    def get_clients_to_list(self):
        return [self.client_pools[id].__str__() for id in self.client_pools]

    def filter_by_epoch(self, epoch: int) -> Dict[str, Client]:
        """Filter the clients by epoch.

        Args:
            epoch (int): The epoch number to filter by.

        Returns:
            Dict[str, Client]: A dictionary of Client objects that have the
                specified epoch number, keyed by client id.
        """

        result: Dict[str, Client] = {}
        client: Client

        # Iterate over the clients in the client_pools attribute
        for client in self.client_pools:
            # If the client's epoch number matches the specified epoch,
            # add it to the result dictionary
            if client.id == epoch:
                result[client.id] = client

        return result

    def filter_finished_clients_by_epoch(self, epoch: int) -> Dict[str, Client]:
        """Filter the finished clients by epoch.

        Args:
            epoch (int): The epoch number to filter by.

        Returns:
            Dict[str, Client]: A dictionary of finished Client objects that
                have the specified epoch number, keyed by client id.
        """

        result: Dict[str, Client] = {}
        client: Client

        # Iterate over the clients in the client_pools attribute
        for id in self.client_pools:
            # If the client's epoch number matches the specified epoch
            # and the client is finished, add it to the result dictionary
            if self.client_pools[id].current_epoch == epoch and self.client_pools[id].is_finished:
                result[id] = self.client_pools[id]

        return result

    def update_local_params(self, msg_obj: UpdateMessage) -> None:
        """Update the local parameters of a client.

        Args:
            msg_obj (UpdateMessage): The message object containing the
                updated client information.
        """

        # Get the client object from the client_pools attribute
        client_id = msg_obj.client_id
        client: Client = self.client_pools[client_id]

        # If the client object exists, update its attributes else
        if client is not None:
            self.client_pools[client_id] = Client(client_id)

        # else we just update all client stage
        self.client_pools[client_id].weight_file = msg_obj.weight_file
        self.client_pools[client_id].current_epoch = msg_obj.epoch
        self.client_pools[client_id].acc = msg_obj.acc
        self.client_pools[client_id].loss = msg_obj.loss
        self.client_pools[client_id].start_time = msg_obj.start
        self.client_pools[client_id].finish_time = time_now()
        self.client_pools[client_id].is_finished = True

    def save_late_update(self, msg_obj: UpdateMessage):
        epoch = msg_obj.epoch
        id = msg_obj.client_id
        client: Client = self.history_state[epoch][id]
        if client is not None:
            self.history_state[epoch][id] = Client(id)

        # else we just update all client stage
        self.history_state[epoch][id].weight_file = msg_obj.weight_file
        self.history_state[epoch][id].current_epoch = msg_obj.epoch
        self.history_state[epoch][id].acc = msg_obj.acc
        self.history_state[epoch][id].loss = msg_obj.loss
        self.history_state[epoch][id].start_time = msg_obj.start
        self.history_state[epoch][id].finish_time = time_now()
        self.history_state[epoch][id].is_finished = True

    def get_available(self):
        """Get the number of available (finished) clients.

        Returns:
            int: The number of clients in the client_pools attribute that
                have the is_finished attribute set to True.
        """

        n_available = 0
        # Iterate over the clients in the client_pools attribute
        client: Client
        for client in self.client_pools:
            # If the client is finished, increment the counter
            if client.is_finished:
                n_available += 1

        return n_available

    def save_history(self, epoch: int):
        """Save the current state of the client_pools attribute to history_state.

        Args:
            epoch (int): The epoch number to associate with the current state.
        """

        # Add the current state of the client_pools attribute to the history_state dictionary

        self.history_state[epoch] = self.client_pools

    def history_to_file(self):
        """_summary_
        """
        path = Config.TMP_FOLDER + "history"
        if not os.path.exists(path):
            os.makedirs(path)
        # write the json object to a text file
        with open("history.txt", "w") as f:
            json.dump(self.history_state, f)

    def reset_client_pools(self):
        """Reset the is_finished attribute of all clients in the client_pools attribute.
        """
        # Iterate over the clients in the client_pools attribute
        client: Client
        for client in self.client_pools:
            # reset all attribute
            client.reset()

    def set_finished_status(self, client_id):
        for id in client_id:
            self.client_pools[id].is_finished = False

    def get_joined_clients(self):
        count = 0
        for i in self.client_pools:
            if self.client_pools[i].is_joined:
                count += 1

        return count
