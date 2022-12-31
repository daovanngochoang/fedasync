from abc import ABC, abstractmethod

from typing import List, Dict, Tuple

import numpy as np

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
        self.global_weight_file: str = "{}.weight.npy".format(self.id)
        self.global_bias_file: str = "{}.bias.npy".format(self.id)

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
        self.tmp = ServerConfig.TMP_FOLDER

    def initialize_parameters(self):
        """Initialize the global parameters.
        """
        self.start_time = time_now()
        self.first_finished = ""
        self.latest_finished = ""
        self.current_epoch += 1

        weight, bias = self.get_model_weight()
        self.save_weight_and_bias_to_file(weight, bias)

        return self.global_weight_file, self.global_bias_file

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

    def save_weight_and_bias_to_file(self, weight: np.ndarray, bias: np.ndarray):
        """
        """
        # save to file
        np.save(self.tmp + self.global_weight_file, weight)
        np.save(self.tmp + self.global_bias_file, bias)

    @abstractmethod
    def get_model_weight(self):
        """

        Returns
        -------

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

        return time_cond or total_finished >= self.min_update_clients

    def start_condition(self, available_clients) -> bool:
        return available_clients >= self.min_fit_clients

    def is_finish(self):
        return self.current_epoch == self.n_epochs
