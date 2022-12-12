
def decode_training_msg(self):
    """Deserialize the training msg in rabbitmq into object when client receive
    that msg it has information about new epoch and global parameters

    input: binary file
    output: class/ json
    """

def encode_update_msg(self):
    """Translate the update msg
    input: class/ json object
    output: binary file
    """

def encode_rececived_notify(self):
    """Translate the received notification received from clients
    input: class/ json object
    output: binary file
    """
