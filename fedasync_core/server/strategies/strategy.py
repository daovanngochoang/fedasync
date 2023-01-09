from abc import ABC, abstractmethod
from typing import List, Dict
from fedasync_core.commons.objects.client import Client
from fedasync_core.commons.utils.time_helpers import *
from fedasync_core.commons.utils.awss3_file_manager import *
import uuid


class Strategy(ABC):

    def __init__(self,
                 model,
                 n_epochs: int,
                 min_update_clients: int,
                 min_fit_clients: int,
                 convergent_value: float,
                 time_rational: float
                 ) -> None:
        self.id = str(uuid.uuid4())
        self.global_weights_file: str = "{}.weights.npy".format(self.id)

        self.model = model
        # the minimum clients to start training process
        self.min_fit_clients = min_fit_clients
        self.min_update_clients = min_update_clients
        self.n_epochs = n_epochs
        self.time_rational = time_rational

        # current server epoch
        self.current_epoch: int = 0

        # the convergent condition value
        self.convergent_value: float = convergent_value

        # starting time of the training process
        self.start_time: str = ""
        self.first_finished: str = ""
        self.latest_finished: str = ""
        self.tmp = Config.TMP_FOLDER
        self.path_to_weights_file = self.tmp + self.global_weights_file

        print(self.min_fit_clients)
        print(self.min_update_clients)

    def initialize_parameters(self):
        """Initialize the global parameters.
        """
        print("Initialize the global parameters.")

        self.start_time = time_now()
        self.first_finished = ""
        self.latest_finished = ""
        self.current_epoch += 1

        return self.global_weights_file

    @abstractmethod
    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        """ Implement the client selection logic by 
        """

    @abstractmethod
    def aggregate(self, join_clients: Dict[str, Client]) -> None:
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    @abstractmethod
    def get_model_weights(self):
        """
        """

    # def save_global_weights(self, weights: np.ndarray):
    #     np.save(self.tmp + self.global_weights_file, weights)
    #
    # def load_global_weights(self):
    #     self.load_weights_file(self.global_weights_file)
    #
    # def load_weights_file(self, file_name):
    #     return np.load(self.tmp + self.global_weights_file)

    def check_update(self, total_finished: int):
        """Check the update condition
            1. We wait until min number of clients are finished
            2. We use the time measurement technique
        """
        time_cond = False
        print("total finished: ", total_finished)
        print("Min clients: ", self.min_update_clients)
        print("total_finished >= self.min_update_clients", total_finished >= self.min_update_clients)

        if total_finished >= self.min_update_clients:
            t1 = time_diff(self.start_time, self.first_finished)
            t2 = time_diff(self.start_time, self.latest_finished)

            # get avg complete time
            avg = (t2 + t1) / total_finished
            time_bound = avg + (self.time_rational * avg)
            print("time_bound: ", time_bound)

            # get time up to now
            now = time_now()
            until_now = time_diff(self.start_time, now)

            time_cond = until_now > time_bound
            print("until_now: ", until_now)

        return time_cond

    def start_condition(self, available_clients) -> bool:
        return available_clients >= self.min_fit_clients

    def is_finish(self):
        return self.n_epochs - self.current_epoch <= 0
