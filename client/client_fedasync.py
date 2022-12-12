from client import Client


class ClientFedAsync(Client):

    def get_properties(self):
        """Return set of client's properties.
        """
        print("Hello the world from Client FedAsync")

    # def get_parameters(self) :
    #     """Return the current local model parameters.
    #     """

    # def fit(self):
    #     """Refine the provided parameters using the locally held dataset.
    #     """

    # def evaluate(self) :
    #     """Evaluate the provided parameters using the locally held dataset.
    #     """
    
instant = ClientFedAsync()
