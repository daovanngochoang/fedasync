from abc import ABC, abstractmethod



class Client(ABC):

    def get_properties(self) :
        """Return set of client's properties.
        """

    def get_parameters(self) :
        """Return the current local model parameters.
        """

    @abstractmethod
    def fit(self):
        """Refine the provided parameters using the locally held dataset.
        """

    @abstractmethod
    def evaluate(self) :
        """Evaluate the provided parameters using the locally held dataset.
        """
    