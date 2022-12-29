from typing import Dict

from commons.objects.messages_objects import UpdateMessage
from commons.objects.client_object import Client


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
        for client in self.client_pools:
            # If the client's epoch number matches the specified epoch
            # and the client is finished, add it to the result dictionary
            if client.id == epoch and client.is_finished:
                result[client.id] = client

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

        self.client_pools[client_id].params_link = msg_obj.param_link
        self.client_pools[client_id].current_epoch = msg_obj.epoch
        self.client_pools[client_id].acc = msg_obj.acc
        self.client_pools[client_id].loss = msg_obj.loss
        self.client_pools[client_id].start_time = msg_obj.start
        self.client_pools[client_id].finish_time = msg_obj.end
        self.client_pools[client_id].is_finished = True

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

    def reset_client_pools(self):
        """Reset the is_finished attribute of all clients in the client_pools attribute.
        """
        # Iterate over the clients in the client_pools attribute
        client: Client
        for client in self.client_pools:
            # reset all attribute
            client.reset()
