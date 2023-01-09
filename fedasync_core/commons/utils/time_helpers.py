# Import the datetime module
from datetime import datetime


def time_diff(time_str_1: str, time_str_2: str) -> float:
    """Calculate the time difference between two time strings in seconds.

    Parameters
    ----------
    time_str_1 : str
        The first time string.
    time_str_2 : str
        The second time string.

    Returns
    -------
    float
        The time difference between the two time strings in seconds.
    """
    # Define the time format
    time_format = "%m/%d/%Y, %H:%M:%S"

    # Convert the time strings to datetime objects
    t1 = datetime.strptime(time_str_1, time_format)
    t2 = datetime.strptime(time_str_2, time_format)

    # Calculate the difference between the two datetime objects
    delta = (t2 - t1).total_seconds()

    return delta


def time_now():
    """Get the current time as a string.

    Returns
    -------
    str
        The current time in the format "%m/%d/%Y, %H:%M:%S".
    """
    # Get the current datetime object
    now = datetime.now()

    # Format the datetime object as a string and return it
    return now.strftime("%m/%d/%Y, %H:%M:%S")
