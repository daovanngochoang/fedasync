




class Server:

    def start(self):
        """
        Start to listen to events from queue server.
        """
    def stop(self):
        """Stop training and release resource
        """


    def redirect(self):
        """Redirect the message to the target function by routing key.
        """


    def translate_message(self):
        """Translate messages in rabbitmq to the target type
        """


    def new_round(self):
        """Start new round
        """


    def check_available_clients(self):
        """Check if worker available before training process
        """

    def send_parameters(self):
        """send the global parameters to clients.
        """

