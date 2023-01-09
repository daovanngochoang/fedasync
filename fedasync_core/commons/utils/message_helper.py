import json
from fedasync_core.commons.objects.messages import UpdateMessage, GlobalMessage


def encode_update_msg(update_message: UpdateMessage) -> str:
    body = {
        'client_id': update_message.client_id,
        'epoch': update_message.epoch,
        'weight_file': update_message.weight_file,
        'acc': update_message.acc,
        'loss': update_message.loss,
        'start': update_message.start,
    }

    # convert to string
    message = json.dumps(body)

    return message


def encode_global_msg(global_message : GlobalMessage) -> str:
    # Create a dictionary with the fields of the object
    body = {
        'chosen_id': global_message.chosen_id,
        'current_epoch': global_message.current_epoch,
        'n_epochs': global_message.n_epochs,
        'weight_file': global_message.weight_file,
    }

    # Convert the dictionary to a JSON string
    body_str = json.dumps(body)

    return body_str


def decode_global_msg(message: bytes) -> GlobalMessage:
    # Convert the message body (bytes) to a string
    body_str = message.decode('utf-8')

    # Parse the message body string as JSON
    body = json.loads(body_str)

    output = GlobalMessage(chosen_id=body["chosen_id"], current_epoch=body["current_epoch"],
                           n_epochs=body['n_epochs'], weight_file=body["weight_file"])

    return output


def decode_update_msg(message: bytes) -> UpdateMessage:
    # Convert the message body (bytes) to a string
    body_str = message.decode('utf-8')

    # Parse the message body string as JSON
    body = json.loads(body_str)

    # Create a new instance of the UpdateMessage class using the fields from the message
    decoded_update_msg = UpdateMessage(
        client_id=body['client_id'], epoch=body["epoch"],
        weight_file=body['weight_file'],
        acc=body['acc'], loss=body['loss'], start=body['start']
    )

    return decoded_update_msg
