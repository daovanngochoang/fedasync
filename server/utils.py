def decode_message():
    """Translate messages in rabbitmq to the target type
    input: binary file
    output: target object (json/ class)
    """

def decode_update_params():
    """Translate the update 
    """


def encode_params(params):
    """Encode global model to binary file
    input: json / class
    output: binary file
    """


from datetime import datetime


def time_diff(timestr1:str, timestr2:str) -> float:
    """
     input: time str with format "%m/%d/%Y, %H:%M:%S"
    """
    format = "%m/%d/%Y, %H:%M:%S"
    t1 = datetime.strptime(timestr1, format)
    t2 = datetime.strptime(timestr2, format)

    delta = (t2 - t1).total_seconds()

    return delta

def time_now ():
    return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")



    
