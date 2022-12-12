

class RoutingRules:
    def __init__(self) -> None:
        
        self.NEW_EPOCH : str = "training.new.epoch"
        self.LOCAL_UPDATE : str = "training.local.update"
        self.AVAILABLE_CLIENT : str = "client.available"
        self.RECEIVED : str = "client.received.model"



class QueueConfig:
    def __init__(self) -> None:
        self.SERVER_QUEUE : str
        self.CLIENT_QUEUE : str
        self.EXCHANGE : str


