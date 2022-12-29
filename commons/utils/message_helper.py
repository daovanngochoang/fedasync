import json
from commons.objects.messages_objects import *


def encode_update_msg(update_message: UpdateMessage) -> str:
    body = {
        'client_id': update_message.client_id,
        'epoch': update_message.epoch,
        'param_link': update_message.param_link,
        'acc': update_message.acc,
        'loss': update_message.loss,
        'start': update_message.start,
        'end': update_message.end
    }

    # convert to string
    message = json.dumps(body)

    return message


def encode_global_msg(global_message : GlobalMessage) -> str:
    # Create a dictionary with the fields of the object
    body = {
        'chosen_id': global_message.chosen_id,
        'epoch': global_message.epoch,
        'param_link': global_message.param_link
    }

    # Convert the dictionary to a JSON string
    body_str = json.dumps(body)

    return body_str


def decode_global_msg(message) -> GlobalMessage:
    # Convert the message body (bytes) to a string
    body_str = message.body.decode('utf-8')

    # Parse the message body string as JSON
    body = json.loads(body_str)
    chosen_id = body["chosen_id"]
    epoch = body["epoch"]
    link = body["param_link"]

    output = GlobalMessage(chosen_id, epoch, link)

    return output


def decode_update_msg(message) -> UpdateMessage:
    # Convert the message body (bytes) to a string
    body_str = message.body.decode('utf-8')

    # Parse the message body string as JSON
    body = json.loads(body_str)

    # Extract the fields from the message body
    client_id = body['client_id']
    epoch = body['epoch']
    param_link = body['param_link']
    acc = body['acc']
    loss = body['loss']
    start = body['start']
    end = body['end']

    # Create a new instance of the UpdateMessage class using the fields from the message
    obj = UpdateMessage(client_id, epoch, param_link, acc, loss, start, end)

    return obj
