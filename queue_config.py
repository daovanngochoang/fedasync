


class RoutingRules:
    def __init__(self) -> None:
        
        # Binding at client queue
        self.NEW_EPOCH : str = "client.training.fit"
        self.CHECK_AVAILABLE_CLIENT : str = "client.available.request"

        # binding at server queue
        self.LOCAL_UPDATE : str = "update.to.server"
        self.AVAILABLE_CLIENT_RESPONE : str = "client.available.response"
        self.RECEIVED_NOTIFY : str = "client.received.model"



class QueueConfig:
    def __init__(self) -> None:
        self.SERVER_QUEUE : str = "server_queue"
        self.CLIENT_QUEUE : str = "client_queue"
        self.EXCHANGE : str = "share_exchange"

