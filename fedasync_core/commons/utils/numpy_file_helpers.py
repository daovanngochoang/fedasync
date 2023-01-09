# Import the NumPy library as np
import numpy as np


def save_array(array, filename):
    """Save a NumPy array to a file.

    Parameters
    ----------
    array : numpy.ndarray
        The NumPy array to save.
    filename : str
        The name of the file to save the array to.
    """
    # Save the array to the specified file using the numpy.save function
    np.save(filename, array)


def load_array(filename):
    """Load a NumPy array from a file.

    Parameters
    ----------
    filename : str
        The name of the file to load the array from.

    Returns
    -------
    numpy.ndarray
        The NumPy array loaded from the file.
    """
    # Load the array from the specified file using the numpy.load function
    return np.load(filename, allow_pickle=True)
