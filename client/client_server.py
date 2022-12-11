from abc import ABC, abstractmethod


class ClientServer:

    def start_listen(self):
        """Listen to training events
        """

    def send_update(self):
        """Send the update for gradients
        """

    def notify(self):
        """Notify the worker when worker receive the global grads.
        """
    
    def send_status(self):
        """When the server want to check if the worker is available?
        """
    
    def send_parameters(self):
        """Send parameters to server
        """
