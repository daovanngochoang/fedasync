# Import the NumPy library as np
import numpy as np
import boto3
from commons.config import ServerConfig

# get tmp folder from config file
tmp = ServerConfig.TMP_FOLDER

# get bucket name
bucket_name = ServerConfig.BUCKET_NAME

# create s3 object with all necessary information
s3 = boto3.resource(
    service_name="s3",
    region_name="ap-southeast-1",
    aws_access_key_id= ServerConfig.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=ServerConfig.AWS_SECRET_ACCESS_KEY
)

# get the target bucket
bucket = s3.Bucket(bucket_name)


def upload_file_to_awss3(file_name: str) -> None:
    """ Upload local file to s3
    Args:
        file_name (String) : Path to the local file
    """
    local_path = tmp + file_name
    bucket.upload_file(Filename=local_path, Key=file_name)


def delete_awss3_file(Key) -> None:
    """Delete file
    Args:
        Key (String): File's name or Key that we want to delete from bucket
    """
    bucket.Object(Key).delete()


def download_awss3_file(file_name: str) -> str:
    """Download file from s3 and save to local

    Args:
        file_name (String): the name of file in s3 bucket

    Returns:
        str: local path of the file after download complete
    """
    local_path = tmp + file_name
    bucket.download_file(file_name, local_path)
    return local_path


def get_all_awss3_file(self) -> list:
    """Get all files from s3

    Returns:
        list: all file name from s3 bucket
    """
    list_files = []
    for f in bucket.objects.all():
        list_files.append(f.key)
    return list_files


def save_nparray_to_file(array: np.ndarray, filename: str) -> None:
    """Save a NumPy array to a file.

    Parameters
    ----------
    array : numpy.ndarray
        The NumPy array to save.
    filename : str
        The name of the file to save the array to.
    """
    # Save the array to the specified file using the numpy.save function
    file_path = tmp + filename
    np.save(file_path, array)


def load_nparray_from_file(filename) -> np.ndarray:
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
    file_path = tmp + filename
    return np.load(file_path)
