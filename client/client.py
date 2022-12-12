from abc import ABC, abstractmethod

class Client(ABC):
    def __init__(self) -> None:
        id: "23432432"

    
    @abstractmethod
    def get_properties(self) :
        """Return set of client's properties.
        """
    @abstractmethod
    def get_params(self) :
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
    