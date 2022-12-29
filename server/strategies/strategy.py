from abc import ABC, abstractmethod

from typing import List, Dict
from commons.objects.client_object import Client
from commons.utils.time_helpers import *
from commons.aws_s3_manager import *
from commons.config import ServerConfig


class Strategy(ABC):

    def __init__(self,
                 params_file,
                 n_epochs: int,
                 min_update_clients: int,
                 min_fit_clients: int,
                 convergent_value: int,
                 time_rational: float
                 ) -> None:
        self.global_params_file: str = params_file

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

        # temp folder hold weights files

    def initialize_parameters(self):
        """Initialize the global parameters.
        """
        self.start_time = time_now()
        self.first_finished = ""
        self.latest_finished = ""

        # upload latest global model
        upload_file(ServerConfig.TMP_FOLDER+self.global_params_file, self.global_params_file)
        return self.global_params_file

    @abstractmethod
    def select_client(self, all_clients: Dict[str, Client]) -> List[str]:
        """ Implement the client selection logic by 
        """

    @abstractmethod
    def aggregate(self, local_params: List[str], join_clients: List[Client]) -> None:
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    def check_update(self, total_finished: int):
        """Check the update condition
            1. We wait until min number of clients are finished
            2. We use the time measurement technique
        """

        time_cond = False

        if self.start_time != self.first_finished != self.latest_finished != "":
            t1 = time_diff(self.start_time, self.first_finished)
            t2 = time_diff(self.start_time, self.latest_finished)

            # get avg complete time
            avg = (t2 + t1) / total_finished
            time_bound = avg + (self.time_rational * avg)

            # get time up to now
            now = time_now()
            until_now = time_diff(self.start_time, now)

            time_cond = time_bound > until_now

        return time_cond or total_finished == self.min_update_clients

    def start_condition(self, available_clients) -> bool:
        return available_clients > self.min_fit_clients

    def is_finish(self):
        return self.current_epoch == self.n_epochs
