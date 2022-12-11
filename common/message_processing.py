

class MessageProcessing():

    def serialize_training_msg(self):
        """serialize the object of new epoch including all information and the global parameters 
            and before server send to client
        """
    def deserialize_training_msg(self):
        """Deserialize the training msg in rabbitmq into object when client receive
        that msg it has information about new epoch and global parameters
        """


    def deserialize_update_msg(self):
        """Translate the update msg received from clients
        """

    def deserialize_rececived_notify(self):
        """Translate the received notification received from clients
        """

    def deserialize_available_msg(self):
        """Translate the available msg received from clients when it listen to the queue
            or when the server check it's available status
        """
    
    def serialize_update_msg(self):
        """serialize the update msg before client send to server
        """

    def serialize_rececived_notify(self):
        """serialize the received notification before client send to server
        """

    def serialize_available_msg(self):
        """serialize the available msg that the client send to server when it listen to the queue
            or when the server check it's available status
        """

    def serialize_training_msg(self):
        """serialize message object to before sending the training signal to clients
        """
    