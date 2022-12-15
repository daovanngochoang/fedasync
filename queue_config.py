

class RoutingRules:

    # Binding at client queue
    NEW_EPOCH : str = "client.training.fit"
    NOTIFY : str = "client.check.available"

    # binding at server queue
    LOCAL_UPDATE : str = "update.to.server"
    CLIENTS_REGISTER : str = "register"
    RECEIVED_NOTIFY : str = "model.received"



class QueueConfig:

    SERVER_QUEUE : str = "server_queue"
    CLIENT_QUEUE : str = "client_queue"
    EXCHANGE : str = "share_exchange"
    


