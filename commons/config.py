class RoutingRules:
    # Binding at client queue
    NEW_EPOCH: str = "client.training.fit"

    # binding at server queue
    LOCAL_UPDATE: str = "update.to.server"
    CLIENTS_REGISTER: str = "register"


class QueueConfig:
    SERVER_QUEUE: str = "server_queue"
    CLIENT_QUEUE: str = "client_queue"
    EXCHANGE: str = "share_exchange"


class ServerConfig:
    TMP_FOLDER = "./tmp/"
