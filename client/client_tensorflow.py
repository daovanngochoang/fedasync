from pika import BlockingConnection

from client.client_server import ClientServer


class ClientTensorflow(ClientServer):
    def __init__(self, model, queue_connection: BlockingConnection):
        super().__init__(model, queue_connection)

    def get_params(self):
        pass

    def fit(self):
        pass

    def evaluate(self):
        pass

